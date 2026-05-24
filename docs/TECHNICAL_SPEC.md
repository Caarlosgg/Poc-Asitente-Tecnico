# Especificación Técnica — POC Asistente Técnico de Diagnóstico

> **Alcance**: Descripción detallada de cada archivo del proyecto, su propósito, funciones clave, dependencias y cómo se interconectan entre sí.  
> **Actualizado**: Mayo 2025

---

## Índice

1. [Visión general de la arquitectura](#1-visión-general-de-la-arquitectura)
2. [Backend — FastAPI](#2-backend--fastapi)
   - 2.1 Punto de entrada y configuración
   - 2.2 Modelos ORM (SQLAlchemy)
   - 2.3 Schemas Pydantic
   - 2.4 Rutas / Endpoints
   - 2.5 Servicios
   - 2.6 Módulos de lógica de negocio
   - 2.7 Base de datos
3. [Frontend — React + Vite](#3-frontend--react--vite)
   - 3.1 Raíz de la aplicación
   - 3.2 Componentes de Chat
   - 3.3 Componentes de UI
   - 3.4 Componentes de Analítica
   - 3.5 Servicios de API
4. [Flujo de datos completo](#4-flujo-de-datos-completo)
5. [Base de datos — esquema](#5-base-de-datos--esquema)
6. [Infraestructura — Docker Compose](#6-infraestructura--docker-compose)
7. [Variables de entorno](#7-variables-de-entorno)

---

## 1. Visión general de la arquitectura

```
┌─────────────────┐      HTTP/REST      ┌──────────────────────┐
│   FRONTEND      │  ─────────────────► │   BACKEND            │
│  React 18.3.1   │                     │   FastAPI 0.115.2    │
│  Vite 5.4.2     │ ◄─────────────────  │   Python 3.12        │
│  Tailwind CSS   │                     │   Uvicorn            │
│  Port 3000      │                     │   Port 8000          │
└─────────────────┘                     └──────────┬───────────┘
                                                   │  SQLAlchemy 2.0 async
                                                   ▼
                                        ┌──────────────────────┐
                                        │  PostgreSQL 16        │
                                        │  + pgvector          │
                                        │  Port 5432           │
                                        └──────────────────────┘
                                                   │
                                        External: Groq API
                                        Model: llama-3.1-8b-instant
```

**Patrón**: Arquitectura de tres capas separadas por contenedores Docker, comunicadas vía HTTP REST. Sin WebSockets — el cliente hace polling / peticiones reactivas.

---

## 2. Backend — FastAPI

### 2.1 Punto de entrada y configuración

#### `backend/app/main.py`
- **Función**: Instancia la app FastAPI, registra routers, configura CORS, health check.
- **Routers montados**:
  - `/session` → `api/routes/session.py`
  - `/metrics` → `api/routes/metrics.py`
  - `/analytics` → `api/routes/analytics.py`
  - `/knowledge` → `api/routes/knowledge.py`
- **CORS**: Origins `*` (POC). En producción se acotaría al dominio frontend.
- **Health check**: `GET /health` → `{ status: "ok", timestamp }`.

#### `backend/core/config.py`
- **Función**: Configuración centralizada mediante `pydantic-settings 2.5.2`.
- **Clase**: `Settings(BaseSettings)` — lee variables de entorno con prefijo `POC_`.
- **Campos clave**:
  - `DATABASE_URL`: conexión asyncpg (`postgresql+asyncpg://...`)
  - `GROQ_API_KEY`: clave API para LLM
  - `GROQ_MODEL`: nombre del modelo (default `llama-3.1-8b-instant`)
  - `LOG_LEVEL`: nivel de logging

#### `backend/core/database.py`
- **Función**: Crea el engine async de SQLAlchemy, la sessionmaker, y el `get_db` Dependency.
- **`create_async_engine`**: Pool de conexiones con `echo=False` en producción.
- **`AsyncSession`**: Cada request FastAPI obtiene una sesión independiente vía `Depends(get_db)`.

#### `backend/core/exceptions.py`
- **Función**: Excepción de dominio `SessionNotFoundError` — lanzada cuando no se encuentra una sesión.

### 2.2 Modelos ORM (SQLAlchemy)

#### `backend/models/session.py`
```
Session
├── session_id: UUID (PK)
├── vin: String(50) FK→vehicles.vin (nullable)
├── model: String(100) — modelo del vehículo
├── entry_point: String(50) — síntoma/ruta de entrada
├── status: String(50) — 'active' | 'closed'
├── started_at: DateTime
├── ended_at: DateTime (nullable)
├── total_steps: Integer
├── final_result: String(255) — diagnóstico final
├── success: Boolean (nullable)
└── Relaciones:
    ├── vehicle → Vehicle (ManyToOne)
    ├── state → SessionState (OneToOne)
    ├── messages → [Message] (OneToMany)
    ├── decision_logs → [DecisionLog] (OneToMany)
    └── feedback → Feedback (OneToOne)

SessionState
├── session_id: UUID (PK, FK→sessions.session_id)
├── vin: String(50) FK→vehicles
├── model: String(100)
├── current_symptom: String(100) — síntoma activo
├── current_node: String(100) — nodo activo del grafo LangGraph
├── state_json: JSONB — estado completo del ConversationState serializado
└── updated_at: DateTime
```

#### `backend/models/message.py`
```
Message
├── message_id: BigInteger (PK, autoincrement)
├── session_id: UUID (FK→sessions.session_id)
├── role: String(20) — 'user' | 'assistant'
├── content: Text — contenido del mensaje
└── created_at: DateTime
```

#### `backend/models/vehicle.py`
```
Vehicle
├── vin: String(50) (PK)
├── model: String(100)
├── year: Integer
├── color: String(50)
├── km: Integer
└── Relaciones → sessions
```

#### `backend/models/knowledge.py`
```
FAQ
├── faq_id: Integer (PK)
├── question: Text
├── answer: Text
├── category: String(100)
├── model: String(100) — 'ALL' o modelo específico
├── tags: JSONB
├── usage_count: Integer
└── embedding: Vector(1536) — pgvector (vacío en POC)

HistoricalCase
├── case_id: String(50) (PK, ej. CASE-001)
├── model: String(100)
├── symptom_category: String(100)
├── case_text: Text — descripción del caso
├── final_diagnosis: String(255)
├── base_confidence: Numeric(5,4)
└── created_at: DateTime

DiagnosticTree
├── tree_id: String(50) (PK, ej. AK550_MOTOR_V1)
├── model: String(100)
├── symptom: String(100)
├── version: String(20)
├── is_active: Boolean
└── created_at: DateTime

TreeNode
├── node_id: String(100) (PK combinado con tree_id)
├── tree_id: FK→diagnostic_trees
├── node_type: String(20) — 'question'|'diagnosis'|'action'
├── content: Text — texto del nodo
├── yes_next: String(100) — siguiente nodo si respuesta Sí
├── no_next: String(100) — siguiente nodo si respuesta No
└── metadata_: JSONB
```

#### `backend/models/feedback.py`
```
Feedback
├── feedback_id: Integer (PK)
├── session_id: UUID (FK→sessions)
├── useful: Boolean
├── comment: Text (nullable)
└── created_at: DateTime
```

#### `backend/models/decision_log.py`
```
DecisionLog
├── log_id: BigInteger (PK)
├── session_id: UUID (FK→sessions)
├── step_number: Integer
├── module_name: String(100)
├── input_summary: Text
├── output_summary: Text
└── created_at: DateTime
```

### 2.3 Schemas Pydantic

#### `backend/api/schemas/session.py`
- **`SessionStartResponse`**: `{ session_id, message, message_type, options }` — respuesta al iniciar sesión.
- **`MessageRequest`**: `{ session_id, message }` — petición del usuario.
- **`DiagnosisData`**: `{ primary_hypothesis, alternatives, next_check, short_explanation, confidence, source_type }` — diagnóstico estructurado.
- **`MessageResponse`**: `{ session_id, message, message_type, options, diagnosis, route, step_number, suggests_tree }` — respuesta del asistente.
- **`MessageSummary`**: `{ role, content, created_at }` — resumen de mensaje para detalle de sesión.
- **`SessionDetailResponse`**: `{ session_id, vin, model, status, total_steps, current_node, current_symptom, started_at, entry_point, final_result, messages[] }` — detalle completo de sesión.

#### `backend/api/schemas/metrics.py`
- **`MetricsSummaryResponse`**: campos de KPIs + `top_diagnoses[]`, `module_usage{}`, `feedback{}`.

### 2.4 Rutas / Endpoints

#### `backend/api/routes/session.py`
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/session/start` | Crea nueva sesión. Llama al grafo LangGraph con el nodo `dispatch`. Retorna saludo + opciones de menú o solicitud de VIN. |
| POST | `/session/message` | Procesa mensaje del usuario. Determina nodo de entrada del grafo, invoca `conversation_graph.invoke()`, persiste mensaje y actualiza estado. |
| GET | `/session/{session_id}` | Devuelve detalle completo de sesión: metadatos + mensajes + entry_point + final_result. |
| POST | `/session/{session_id}/feedback` | Registra feedback (útil/no útil + comentario) en tabla `feedback`. |

**Lógica interna de `POST /session/message`**:
1. Valida UUID del session_id.
2. Carga `Session` y `SessionState` de BD.
3. Llama a `_determine_entry_node()` para decidir qué nodo del grafo invocar.
4. Construye el `ConversationState` desde el `state_json`.
5. Invoca `conversation_graph.invoke(state, config={entry: nodo})`.
6. Parsea el `output_state` para construir `MessageResponse`.
7. Persiste el mensaje del usuario y la respuesta del asistente (`save_message`).
8. Actualiza `session_state` y opcionalmente `session.status/final_result`.

#### `backend/api/routes/metrics.py`
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/metrics/summary` | KPIs globales: totales, tasa de éxito, promedio de pasos, duración media, uso por módulo, top diagnósticos, feedback positivo/negativo. |

**Implementación**: Múltiples queries SQL agregadas (`func.count`, `func.avg`), sin tocar datos.

#### `backend/api/routes/analytics.py`
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/analytics/sessions` | Lista paginada de sesiones con `limit`, `offset`, `status` filter. |
| GET | `/analytics/diagnoses` | Ranking de `final_result` más frecuentes agrupado por modelo. |
| GET | `/analytics/feedback` | Lista paginada de feedback con resumen positivo/negativo. |
| GET | `/analytics/heatmap` | Matriz síntomas × modelos: combina `sessions.entry_point` + `historical_cases.symptom_category`. Devuelve `{ models[], symptoms[], rows[], max_value }`. |

#### `backend/api/routes/knowledge.py`
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/knowledge/faqs` | Lista de FAQs con filtros opcionales por `model` y `category`. |
| GET | `/knowledge/cases` | Lista de casos históricos con filtro por `model`. |
| GET | `/knowledge/trees` | Lista de árboles DDT activos con recuento de nodos. |

### 2.5 Servicios

#### `backend/services/tracing.py`
- **`save_message(db, session_id, role, content)`**: Inserta registro en tabla `messages`.
- **`increment_session_steps(db, session_id)`**: Incrementa `total_steps` de la sesión.
- **`log_decision(db, session_id, step, module, input_summary, output_summary)`**: Registra en `decision_logs`.
- **Uso**: Llamado desde `session.py` tras cada turno de conversación.

#### `backend/services/session_flow.py`
- Lógica auxiliar para determinar si una sesión debe cerrarse o reconducirse tras diagnóstico.

#### `backend/services/tree_engine.py`  
- Wrapper que carga y navega nodos del árbol DDT desde BD. Llama a `TreeNode` para avanzar por el árbol según la respuesta del usuario.

### 2.6 Módulos de lógica de negocio

Ubicados en `backend/modules/`. Cada módulo es un paquete Python independiente que implementa una capacidad del asistente. El grafo LangGraph los coordina.

#### `backend/modules/orchestrator/`
- **`graph.py`**: Define el `StateGraph(ConversationState)` de LangGraph.
  - **Nodos del grafo**:
    | Nodo | Función |
    |------|---------|
    | `dispatch` | Punto de entrada. Decide si pedir VIN o mostrar menú. |
    | `vin_lookup` | Verifica el VIN contra la tabla `vehicles`. |
    | `request_vin` | Solicita el VIN al usuario si no está identificado. |
    | `show_menu` | Genera las opciones del menú de síntomas. |
    | `classifier_node` | Clasifica la intención del usuario (síntoma, FAQ, texto libre). |
    | `await_input_node` | Nodo de espera — el grafo para aquí y espera el siguiente mensaje. |
    | `tree_engine` | Ejecuta el árbol DDT paso a paso. |
    | `faq_matcher` | Busca en la base de FAQs (lexical, sin embeddings). |
    | `free_text_node` | Procesa descripción libre con historial de casos + LLM. |
    | `session_end_error` | Termina la sesión en error. |
  - **Aristas**: Definidas con `add_conditional_edges` y `add_edge`. El flujo es dirigido pero con bifurcaciones condicionales.

- **`state.py`**: Clase `ConversationState(TypedDict)` — estado completo de la conversación:
  - `session_id`, `vin`, `model`, `messages`, `current_node`, `current_symptom`
  - `facts`, `active_hypotheses`, `tree_id`, `current_tree_node`
  - `final_diagnosis`, `route`, `output_message`, `output_options`

#### `backend/modules/vin_lookup/`
- Nodo que consulta `SELECT * FROM vehicles WHERE vin = ?` para validar y obtener modelo.

#### `backend/modules/tree_engine/`
- Carga el árbol DDT activo para el síntoma detectado, navega nodos, genera preguntas Sí/No.
- Persiste el nodo actual en `session_state.current_node` para retomar en el siguiente mensaje.

#### `backend/modules/faq_matcher/`
- Búsqueda lexical (sin vectores) en `faqs`: tokenización simple + jaccard/contains.
- Devuelve la mejor FAQ con su respuesta formateada.

#### `backend/modules/free_text_parser/`  
- Recibe texto libre del usuario, busca en `historical_cases` por similitud de texto, llama al LLM (Groq) para sintetizar el diagnóstico.

#### `backend/modules/hybrid_ranking/`
- Combina scores de múltiples fuentes (FAQ, historial, árbol) para seleccionar la mejor respuesta.

#### `backend/modules/response_builder/`
- Formatea el diagnóstico final en un `DiagnosisData` estructurado, asegurando que todos los campos requeridos estén presentes.

#### `backend/modules/session_state/`
- Helpers para leer y escribir el `state_json` en `session_state`. Convierte entre `ConversationState` (TypedDict) y JSON serializable.

#### `backend/modules/historical_retrieval/`
- Recupera casos históricos de la tabla `historical_cases` por modelo y categoría.

#### `backend/modules/feedback_metrics/`
- Lógica de agregación para el endpoint `/metrics/summary`.

#### `backend/modules/traceability/`
- Gestión de `decision_logs`: registra cada decisión del grafo con módulo, entrada y salida.

### 2.7 Base de datos

#### `backend/db/schema.py`  
- DDL inicial de todas las tablas. Referencia para recrear el esquema.

#### `backend/db/session.py`
- Alias o helper para obtener la sesión de BD (uso interno de módulos).

#### `backend/db/migrations/`
- SQL plano para migraciones manuales (no Alembic en POC).

#### `backend/db/seeds/`
- Scripts SQL para poblar datos de prueba:
  - `consumo_tree.sql` — Árbol AK550_CONSUMO_V1 (15 nodos)
  - `historical_cases_enrichment.sql` — 25 casos adicionales (CASE-052..076)
  - `faqs_enrichment.sql` — 14 FAQs adicionales
  - `vehicles_enrichment.sql` — 29 VINs adicionales (44 total, 6 modelos)

---

## 3. Frontend — React + Vite

### 3.1 Raíz de la aplicación

#### `frontend/src/main.jsx`
- Monta `<App />` en el DOM. Import de `index.css`.

#### `frontend/src/App.jsx`
- **Función**: Layout raíz de la SPA. Compone la pantalla completa en tres zonas:
  1. **Header**: barra superior con icono de vehículo, nombre del sistema, indicador de salud (`HealthIndicator`).
  2. **Left sidebar**: `<LeftNavSidebar />` (analítica, siempre visible, colapsable a iconos).
  3. **Área de chat**: `<PhaseBar />` (progreso del árbol) + `<ChatContainer />`.
- **Estado**: `chatPhase` (string) — propagado hacia abajo para `PhaseBar`.
- **Estructura CSS**: `h-screen bg-gray-950 flex flex-col overflow-hidden` → header → `flex flex-1 overflow-hidden` → sidebar + chat.

#### `frontend/src/index.css`
- Directivas Tailwind (`@tailwind base/components/utilities`).
- `.scrollbar-thin` — scrollbar personalizado con `scrollbar-color`.
- `.animate-fade-in` + `@keyframes fadeIn` — aparición suave de mensajes (opacity 0→1, translateY 6px→0, 0.2s).

### 3.2 Componentes de Chat

#### `frontend/src/components/Chat/ChatContainer.jsx`
- **Función**: Componente orquestador del chat. Gestiona toda la lógica conversacional en el frontend.
- **Estado local**:
  - `messages[]` — lista de mensajes mostrados
  - `sessionId` — UUID de la sesión activa (persistido en `localStorage`)
  - `options[]` — opciones de menú actuales
  - `isLoading` — spinner durante respuesta del backend
  - `phase` — fase del árbol DDT para `PhaseBar`
  - `showSummary` — controla visibilidad de `SessionSummaryPanel`
- **Flujo de inicio**: 
  1. En mount, llama `startSession()`.
  2. Recibe `{ session_id, message, options }`.
  3. Muestra mensaje de bienvenida.
- **Flujo de mensaje**:
  1. Usuario escribe en `InputBar` o selecciona opción de `MenuOptions`/`QuickReplies`.
  2. Añade mensaje de usuario a `messages[]`.
  3. Llama `sendMessage(sessionId, texto)`.
  4. Recibe `MessageResponse` — añade respuesta del asistente.
  5. Si `message_type === 'diagnosis'`, muestra `DiagnosisResult` + `QuickReplies` (feedback, resumen).
  6. Si `message_type === 'menu'`, muestra `MenuOptions`.
- **Scroll fix**: El div padre del scrollable usa `overflow-hidden` y el div de mensajes tiene `overflow-y-auto min-h-0` (el `min-h-0` en el padre flex es crítico para que el scroll funcione en Firefox/Chrome).

#### `frontend/src/components/Chat/MessageBubble.jsx`
- **Función**: Renderiza un mensaje individual.
- **Props**: `role` ('user'|'assistant'), `content` (string).
- **Diseño**: 
  - Usuario: burbuja azul a la derecha, icono de persona.
  - Asistente: burbuja gris oscuro a la izquierda, icono de robot.
  - Animación: `animate-fade-in` con retraso escalonado.

#### `frontend/src/components/Chat/MenuOptions.jsx`
- **Función**: Menú visual de selección de síntomas/rutas. Se muestra cuando `message_type === 'menu'`.
- **`OPTION_META`**: Diccionario que enriquece cada `option.id` con icono emoji, descripción, gradiente de color, borde, badge de ruta (A/B/C).
- **Layout**:
  - Síntomas principales (motor, arranque, celp, consumo) → grid 2 columnas con tarjetas grandes.
  - Opciones especiales (faq, other) → ancho completo horizontal con icono a la izquierda.
- **Interactividad**: Hover con `translate-y-0.5`, `ring`, glow shadow por color de ruta.
- **`ROUTE_LABELS`**: Mapeo A→árbol DDT, B→FAQ, C→IA libre.

#### `frontend/src/components/Chat/InputBar.jsx`
- **Función**: Barra de entrada de texto. Textarea autoexpandible + botón enviar.
- **Props**: `onSend(text)`, `disabled`.
- **SVG**: Icono de flecha "enviar" SVG inline (sin dependencia de iconset).

#### `frontend/src/components/Chat/QuickReplies.jsx`
- **Función**: Botones de respuesta rápida (Sí/No en árboles, "Ver resumen", "Nueva consulta").
- **Props**: `options[]`, `onSelect(id, label)`.

#### `frontend/src/components/Chat/DiagnosisResult.jsx`
- **Función**: Card visual del diagnóstico final. Muestra `primary_hypothesis`, `alternatives[]`, `confidence`, `next_check`, `short_explanation`, badge de `source_type`.

#### `frontend/src/components/Chat/RouteHeader.jsx`
- **Función**: Cabecera de sección insertada en el flujo de mensajes al cambiar de ruta (Árbol / FAQ / Libre).

#### `frontend/src/components/Chat/ReconductionCard.jsx`
- **Función**: Tarjeta que aparece cuando el backend sugiere reconducir a un árbol DDT desde la ruta C.

### 3.3 Componentes de UI

#### `frontend/src/components/UI/SessionSummaryPanel.jsx`
- **Función**: Modal flotante `position: fixed` con el resumen completo de una sesión.
- **Activación**: Botón "Ver resumen" en `ChatContainer` tras diagnóstico.
- **Datos cargados**: `GET /session/{sessionId}` → `SessionDetailResponse`.
- **Secciones mostradas**:
  1. Vehículo: VIN + modelo.
  2. Estadísticas: total_steps, nº de mensajes, estado (✓/…).
  3. Ruta de diagnóstico: árbol/FAQ/libre con icono.
  4. Diagnóstico final: texto de `final_result`.
  5. Conversación: lista de mensajes `role/content`.

#### `frontend/src/components/UI/HealthIndicator.jsx`
- **Función**: Indicador de estado del backend en el header. Puntito verde/rojo.
- **Implementación**: `GET /health` periódico cada 30 segundos.

#### `frontend/src/components/UI/PhaseBar.jsx`
- **Función**: Barra de progreso del árbol DDT (F4). Muestra paso actual dentro del árbol.
- **Props**: `phase` (objeto con `step`, `total`, `label`).

#### `frontend/src/components/UI/TreeProgressBar.jsx`
- **Función**: Barra visual del nodo actual en el árbol DDT.

### 3.4 Componentes de Analítica

#### `frontend/src/components/Analytics/LeftNavSidebar.jsx`
- **Función**: Sidebar izquierdo permanente con 7 secciones en acordeón.
- **Secciones**:
  | ID | Icono | Contenido |
  |----|-------|-----------|
  | `metrics` | 📊 | KPIs globales (sesiones, módulos, feedback, top diagnósticos) |
  | `sessions` | 🗂️ | Lista últimas 10 sesiones |
  | `diagnoses` | 🔎 | Ranking diagnósticos con barras de progreso |
  | `feedback` | 💬 | Resumen + lista de valoraciones |
  | `knowledge` | 📚 | Sub-tabs: Árboles / FAQs / Casos |
  | `heatmap` | 🌡️ | Mapa de calor síntomas × modelos |
  | `export` | 📄 | Exportar informe PDF |
- **Lazy loading**: Cada sección carga sus datos solo cuando se abre.
- **Colapsado**: A 44px de ancho con solo iconos — cada icono abre su sección directamente.
- **Hook `useApiData`**: Hook genérico reutilizable para fetching con estados `loading`/`error`/`data`.

#### `frontend/src/components/Analytics/SymptomHeatMap.jsx`
- **Función**: Grid visual síntomas × modelos coloreado por frecuencia.
- **Datos**: `GET /analytics/heatmap`.
- **Colores**: Verde (bajo) → Amarillo → Naranja → Rojo (crítico) según `value/max_value`.
- **Tooltip**: Flotante al hover sobre cada celda mostrando modelo, síntoma y cantidad.
- **Tabla HTML**: `<table>` con `<th>` por modelo y `<td>` por síntoma. Cada celda es un `<div>` con clases Tailwind dinámicas.

#### `frontend/src/components/Analytics/PdfExport.jsx`
- **Función**: Genera un informe HTML descriptivo y abre el diálogo de impresión del navegador (sin librería externa).
- **Datos recopilados**: métricas, últimas 50 sesiones, diagnósticos, últimas 50 valoraciones — todo en paralelo con `Promise.all`.
- **HTML generado**: `buildHtml()` — documento completo con KPIs, tablas, estilos inline, sección `@media print`.
- **Apertura**: `window.open()` → `win.document.write(html)` → `win.print()` tras 600ms.

### 3.5 Servicios de API

#### `frontend/src/services/api.js`
- **BASE_URL**: `import.meta.env.VITE_API_URL || ''` (proxy Vite en dev, relativo en prod).
- **`apiFetch(path, options)`**: Helper genérico con manejo de errores HTTP y parseo JSON.
- **Funciones exportadas**:

| Función | Endpoint | Descripción |
|---------|----------|-------------|
| `startSession()` | POST `/session/start` | Inicia sesión nueva |
| `sendMessage(sessionId, msg)` | POST `/session/message` | Envía mensaje |
| `getSession(sessionId)` | GET `/session/{id}` | Detalle de sesión |
| `submitFeedback(id, useful, comment)` | POST `/session/{id}/feedback` | Registra feedback |
| `getMetrics()` | GET `/metrics/summary` | KPIs globales |
| `checkHealth()` | GET `/health` | Estado del backend |
| `getAnalyticsSessions(limit)` | GET `/analytics/sessions` | Lista sesiones |
| `getAnalyticsDiagnoses()` | GET `/analytics/diagnoses` | Ranking diagnósticos |
| `getAnalyticsFeedback(limit)` | GET `/analytics/feedback` | Lista feedback |
| `getKnowledgeFaqs(filters)` | GET `/knowledge/faqs` | FAQs |
| `getKnowledgeCases(filters)` | GET `/knowledge/cases` | Casos históricos |
| `getKnowledgeTrees()` | GET `/knowledge/trees` | Árboles DDT |
| `getHeatmap()` | GET `/analytics/heatmap` | Datos mapa de calor |

---

## 4. Flujo de datos completo

### Inicio de sesión
```
Usuario abre app
→ App.jsx monta ChatContainer
→ ChatContainer.useEffect → startSession()
→ POST /session/start
→ session.py crea Session en BD (UUID generado)
→ Invoca grafo LangGraph en nodo 'dispatch'
→ dispatch decide: sin VIN → output 'Bienvenido, introduce tu número de bastidor'
→ Respuesta: { session_id, message, message_type: 'text', options: null }
→ ChatContainer añade mensaje asistente
→ Muestra InputBar
```

### Identificación de VIN
```
Usuario escribe VIN (ej. "AK550-2023-001")
→ sendMessage(sessionId, "AK550-2023-001")
→ POST /session/message
→ _determine_entry_node() → 'vin_lookup'
→ grafo ejecuta nodo vin_lookup
→ vin_lookup consulta SELECT * FROM vehicles WHERE vin = 'AK550-2023-001'
→ Encontrado: model='AK550 2023', actualiza session.vin y session.model
→ Siguiente nodo: 'show_menu'
→ show_menu genera options: [symptom_motor, symptom_arranque, symptom_celp, symptom_consumo, faq, other]
→ Respuesta: { message_type: 'menu', options: [...] }
→ Frontend muestra MenuOptions
```

### Diagnóstico por árbol DDT (Ruta A)
```
Usuario selecciona 'symptom_motor' → sendMessage(sessionId, "Paradas de motor")
→ _determine_entry_node() → 'classifier_node'
→ classifier_node → identifica síntoma motor → enruta a 'tree_engine'
→ tree_engine: busca árbol activo para model='AK550 2023' + symptom='motor'
→ Carga nodo raíz del árbol (ej. q1: "¿El motor se para en caliente?")
→ Guarda current_node='q1' en session_state.state_json
→ Respuesta: { message_type: 'question', message: "¿El motor se para en caliente?", options: [Sí, No] }

Usuario responde "Sí"
→ tree_engine retoma desde current_node='q1', rama yes_next='q3'
→ Avanza al nodo q3: "¿Aparece humo blanco por el escape?"
→ ... (varios pasos)

Nodo final (type='diagnosis'):
→ tree_engine extrae diagnóstico del nodo
→ response_builder construye DiagnosisData
→ session.final_result = primary_hypothesis
→ session.status = 'closed'
→ Respuesta: { message_type: 'diagnosis', diagnosis: DiagnosisData }
→ Frontend muestra DiagnosisResult + QuickReplies
```

---

## 5. Base de datos — esquema

### Tablas y relaciones

```
vehicles (vin PK)
    └──< sessions (vin FK)
              └──< messages (session_id FK)
              └──1 session_state (session_id PK/FK)
              └──< decision_logs (session_id FK)
              └──1 feedback (session_id FK)

diagnostic_trees (tree_id PK)
    └──< tree_nodes (tree_id FK, node_id PK)

faqs (faq_id PK)
historical_cases (case_id PK)
```

### Volumen de datos (POC)
| Tabla | Registros |
|-------|-----------|
| vehicles | 44 |
| diagnostic_trees | 5 |
| tree_nodes | ~70 nodos |
| faqs | 40 |
| historical_cases | 76 |

### Índices relevantes
- `sessions.vin` (FK → vehicles)
- `sessions.status`
- `messages.session_id`
- `tree_nodes.tree_id`
- `historical_cases.model`
- `faqs.model`, `faqs.category`

---

## 6. Infraestructura — Docker Compose

### `docker-compose.yml`

```yaml
services:
  poc-postgres:    # PostgreSQL 16 + pgvector
    image: pgvector/pgvector:pg16
    port: 5432
    volumes: [postgres_data]
    healthcheck: pg_isready

  poc-backend:     # FastAPI + Uvicorn
    build: ./backend
    port: 8000
    depends_on: [poc-postgres]
    env_file: .env

  poc-frontend:    # React build servido con `serve`
    build: ./frontend
    port: 3000
    depends_on: [poc-backend]
```

### Dockerfiles

**Backend** (`backend/Dockerfile`):
```
FROM python:3.12-slim
WORKDIR /app
RUN apt-get install -y libpq-dev gcc
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend** (`frontend/Dockerfile`):
```
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:20-alpine
RUN npm install -g serve
COPY --from=builder /app/dist ./dist
CMD ["serve", "-s", "dist", "-l", "3000"]
```

### Comandos habituales

```bash
# Arrancar todo
docker compose up -d

# Rebuild tras cambios
docker compose up -d --build frontend backend

# Ver logs
docker compose logs -f backend
docker compose logs -f frontend

# Cargar seed SQL
docker exec -i poc-postgres psql -U poc_user -d poc_asistente < backend/db/seeds/faqs_enrichment.sql

# Shell en backend (debug)
docker exec -it poc-backend bash

# Reiniciar solo backend
docker compose restart backend
```

---

## 7. Variables de entorno

Fichero `.env` en la raíz del proyecto:

```env
# Base de datos
POSTGRES_DB=poc_asistente
POSTGRES_USER=poc_user
POSTGRES_PASSWORD=poc_password
DATABASE_URL=postgresql+asyncpg://poc_user:poc_password@poc-postgres:5432/poc_asistente

# Groq LLM
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-8b-instant

# Frontend (Vite)
VITE_API_URL=http://localhost:8000
```

> **Nota**: El frontend en producción Docker usa ruta relativa `/` (vacío) porque `serve` está en el mismo host que el proxy inverso. En desarrollo local con Vite dev server se usa `http://localhost:8000`.

---

## Dependencias principales

### Backend (`requirements.txt`)
| Paquete | Versión | Uso |
|---------|---------|-----|
| fastapi | 0.115.2 | Framework web |
| uvicorn | latest | Servidor ASGI |
| sqlalchemy | 2.0.x | ORM async |
| asyncpg | latest | Driver PostgreSQL async |
| pydantic | 2.x | Validación de datos |
| pydantic-settings | 2.5.2 | Configuración desde env |
| langgraph | 0.2.28 | Grafo de conversación |
| langchain-core | latest | Abstracciones LLM |
| groq | 0.11.0 | Cliente Groq API |
| pgvector | latest | Extensión vectorial (inactiva en POC) |

### Frontend (`package.json`)
| Paquete | Versión | Uso |
|---------|---------|-----|
| react | 18.3.1 | UI framework |
| react-dom | 18.3.1 | Renderizado DOM |
| vite | 5.4.2 | Bundler / dev server |
| tailwindcss | 3.x | Estilos utility-first |
| autoprefixer | latest | Post-CSS |

---

*Documento generado automáticamente — Mayo 2025*
