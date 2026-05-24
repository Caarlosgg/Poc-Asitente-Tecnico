# ESTUDIAR — Guía completa del proyecto para entender y explicar

> Documento de estudio personal. Explica qué hace el sistema, cómo funciona por dentro,
> qué tecnologías usamos, por qué las elegimos y cómo encaja todo.

---

## ÍNDICE

1. [¿Qué es este proyecto?](#1-qué-es-este-proyecto)
2. [El DDT — corazón del sistema](#2-el-ddt--corazón-del-sistema)
3. [Las tres rutas de diagnóstico](#3-las-tres-rutas-de-diagnóstico)
4. [Flujo completo paso a paso](#4-flujo-completo-paso-a-paso)
5. [La base de datos explicada](#5-la-base-de-datos-explicada)
6. [Arquitectura del sistema](#6-arquitectura-del-sistema)
7. [Tecnologías: qué son, cómo funcionan y por qué las usamos](#7-tecnologías-qué-son-cómo-funcionan-y-por-qué-las-usamos)
   - LangGraph
   - LLM / Groq
   - FastAPI
   - PostgreSQL + pgvector
   - React + Vite + Tailwind
   - Docker
8. [Panel de analítica](#8-panel-de-analítica)
9. [Preguntas que puede hacer tu jefe](#9-preguntas-que-puede-hacer-tu-jefe)

---

## 1. ¿Qué es este proyecto?

Es un **asistente conversacional para técnicos de taller** que ayuda a diagnosticar averías en motocicletas. El técnico:

1. Introduce el número de bastidor (VIN) de la moto
2. El sistema identifica el modelo
3. El técnico elige el síntoma que tiene
4. El asistente le hace preguntas Sí/No y llega a un diagnóstico

También puede hacer preguntas de mantenimiento (FAQs) o describir el problema libremente y la IA lo analiza.

**Por qué es una POC y no un producto final:**
- Usa datos de prueba (VINs ficticios, no el sistema real del fabricante)
- Árboles de diagnóstico solo para AK550 y Xciting 400
- Sin login ni autenticación
- El objetivo es demostrar que la idea funciona antes de invertir en el producto completo

---

## 2. El DDT — corazón del sistema

### ¿Qué significa DDT?

**DDT = Decision Diagnostic Tree** (Árbol de Decisión Diagnóstica)

Es un protocolo técnico estructurado que define cómo diagnosticar una avería siguiendo una secuencia de preguntas binarias (Sí/No). Lo define el fabricante o el equipo técnico y garantiza que el diagnóstico es reproducible y correcto.

### ¿Cómo está estructurado un árbol?

```
                    NODO RAÍZ (q1)
                "¿El motor se para en caliente?"
                       /            \
                     SÍ             NO
                     /               \
                  q3                 q2
         "¿Humo negro          "¿Se para al
          por escape?"          dar gas?"
           /      \              /      \
         SÍ       NO           SÍ       NO
          |        |            |        |
      DIAGNÓSTICO  q5       DIAGNÓSTICO  q4
    "Inyector       ...    "Obstrucción    ...
     defectuoso"            carburador"
```

Cada **nodo** tiene:
- `node_type`: pregunta | diagnóstico | acción
- `content`: el texto de la pregunta o diagnóstico
- `yes_next`: ID del siguiente nodo si la respuesta es Sí
- `no_next`: ID del siguiente nodo si la respuesta es No

Cuando se llega a un nodo de tipo `diagnosis`, se termina el árbol y se devuelve el resultado.

### Árboles disponibles en el sistema

| ID del árbol | Modelo | Síntoma | Nodos |
|---|---|---|---|
| AK550_MOTOR_V1 | AK550 2023 | Paradas de motor | ~15 |
| AK550_ARRANQUE_V1 | AK550 2023 | Problemas de arranque | ~12 |
| AK550_CELP_V1 | AK550 2023 | Testigo CELP encendido | ~10 |
| AK550_CONSUMO_V1 | AK550 2023 | Consumo excesivo | ~15 |
| XCITING400_MOTOR_V1 | Xciting 400 | Paradas de motor | ~10 |

### ¿Por qué el DDT y no simplemente el LLM?

| DDT (árbol) | LLM solo |
|---|---|
| Diagnóstico reproducible | Puede variar entre sesiones |
| Basado en protocolo oficial | Puede "alucinar" o inventar |
| Auditable paso a paso | Caja negra |
| Sin coste de API | Coste por token |
| Funciona sin internet | Necesita Groq/OpenAI |

El LLM se usa **solo en la Ruta C** (texto libre) como apoyo, no como motor principal.

### Principios de diseño del DDT (reglas de negocio)

| Código | Regla |
|---|---|
| RN-NEG-001 | Sin VIN válido no hay diagnóstico |
| RN-NEG-002 | El modelo lo determina el VIN, nunca el texto del usuario |
| RN-NEG-003 | Síntoma conocido → prioridad al árbol DDT (Ruta A) |
| RN-NEG-006 | En Ruta C, los históricos se filtran por modelo del vehículo |
| RN-NEG-009 | Máximo 3 intentos de VIN antes de cerrar sesión en error |

---

## 3. Las tres rutas de diagnóstico

```
MENÚ DE SÍNTOMAS
      │
      ├── ⚡ Paradas de motor    ─────┐
      ├── 🔑 Problemas arranque  ────┤──► RUTA A: Árbol DDT
      ├── ⚠️  Testigo CELP        ────┤     Preguntas Sí/No
      └── ⛽ Consumo excesivo    ─────┘     Protocolo oficial
                                            Diagnóstico exacto
      ├── 📚 Consulta FAQ        ──────► RUTA B: Base de FAQs
                                           Respuesta inmediata
                                           Sin preguntas
      └── 💬 Descripción libre   ──────► RUTA C: IA + Historial
                                           Búsqueda en 76 casos
                                           LLM analiza texto
                                           Sugiere árbol si aplica
```

### Ruta A — Árbol DDT
- El sistema navega nodo a nodo del árbol
- El estado actual (nodo en que estamos) se guarda en BD entre mensajes
- Si el usuario cierra y vuelve, el árbol continúa donde lo dejó
- Al llegar al diagnóstico: muestra `primary_hypothesis`, `alternatives[]`, `confidence`, `next_check`

### Ruta B — FAQs
- Búsqueda lexical en tabla `faqs` (40 registros)
- No usa IA, es instantáneo
- Devuelve la FAQ más relevante para el modelo del vehículo
- Ejemplos: "¿Cada cuánto se cambia el aceite?", "¿Qué hace la luz CELP?"

### Ruta C — Texto libre con IA
- El técnico describe el problema con sus palabras
- El sistema busca en `historical_cases` (76 casos) por similitud de texto
- Si encuentra casos similares, los usa como contexto
- Llama al LLM (Groq) para sintetizar el diagnóstico
- Si detecta que encaja con un árbol DDT, muestra tarjeta de reconducción a Ruta A

---

## 4. Flujo completo paso a paso

```
┌──────────────────────────────────────────────────────────────────┐
│  TÉCNICO abre la app en el navegador (http://localhost:3000)     │
└─────────────────────────┬────────────────────────────────────────┘
                          │  React hace POST /session/start
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│  BACKEND crea una nueva sesión en BD (UUID generado)             │
│  LangGraph entra en nodo 'dispatch'                              │
│  dispatch: no hay VIN → enviar saludo + pedir bastidor           │
└─────────────────────────┬────────────────────────────────────────┘
                          │  React muestra bienvenida
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│  Técnico escribe el VIN (ej. "AK550-2023-001")                   │
└─────────────────────────┬────────────────────────────────────────┘
                          │  POST /session/message {message: "AK550-2023-001"}
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│  Backend: _determine_entry_node() → nodo 'vin_lookup'            │
│  vin_lookup: SELECT * FROM vehicles WHERE vin='AK550-2023-001'   │
│  ✓ Encontrado → model='AK550 2023'                               │
│  Guarda vin y model en session + session_state                   │
│  Siguiente nodo → 'show_menu'                                    │
│  show_menu: genera lista de 6 opciones                           │
└─────────────────────────┬────────────────────────────────────────┘
                          │  Respuesta: {message_type: 'menu', options: [...]}
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│  React muestra MenuOptions (tarjetas visuales con emojis)        │
│  ⚡ Paradas de motor  🔑 Arranque  ⚠️ CELP  ⛽ Consumo            │
│  📚 FAQ                           💬 Texto libre                  │
└─────────────────────────┬────────────────────────────────────────┘
                          │  Técnico selecciona "⚡ Paradas de motor"
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│  POST /session/message {message: "Paradas de motor"}             │
│  _determine_entry_node() → 'classifier_node'                     │
│  classifier: detecta síntoma_motor → enruta a 'tree_engine'      │
│  tree_engine: busca árbol activo para AK550 + motor              │
│  Carga nodo raíz: q1 "¿El motor se para en caliente?"            │
│  Guarda current_node='q1' en session_state                       │
└─────────────────────────┬────────────────────────────────────────┘
                          │  Respuesta: {message_type: 'question', options: [Sí, No]}
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│  Técnico responde "Sí"                                           │
│  tree_engine: carga nodo actual (q1), rama yes_next='q3'         │
│  Siguiente pregunta: "¿Aparece humo negro por el escape?"        │
│  ... (varios pasos Sí/No)                                        │
└─────────────────────────┬────────────────────────────────────────┘
                          │  Nodo de tipo 'diagnosis'
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│  DIAGNÓSTICO FINAL                                               │
│  primary_hypothesis: "Válvula EGR obstruida"                     │
│  confidence: 0.87                                                │
│  next_check: "Inspeccionar circuito EGR"                         │
│  session.final_result = "Válvula EGR obstruida"                  │
│  session.status = 'closed'                                       │
└─────────────────────────┬────────────────────────────────────────┘
                          │  Respuesta: {message_type: 'diagnosis', diagnosis: {...}}
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│  React muestra DiagnosisResult (tarjeta visual)                  │
│  Técnico pulsa 👍 o 👎 → POST /session/{id}/feedback             │
│  Opción: "Ver resumen" → abre SessionSummaryPanel (modal)        │
└──────────────────────────────────────────────────────────────────┘
```

### Flujo del grafo LangGraph (simplificado)

```
         [dispatch]
              │
       ¿Tiene VIN?
      No/         \Sí
        ▼           ▼
  [request_vin]  [show_menu]
        │              │
   usuario         usuario
   da VIN          elige
        │              │
  [vin_lookup]    [classifier_node]
        │              │
  ¿VIN válido?    ¿Qué intención?
  Sí ──►show_menu  ├── síntoma → [tree_engine]
  No ──►pedir otra │── faq     → [faq_matcher]
  3× ──►error      └── libre   → [free_text_node]
                        │              │            │
                   nodo árbol     FAQ match    LLM + historial
                        │              │            │
                        └──────────────┴────────────┘
                                       │
                              [response_builder]
                                       │
                              Diagnóstico formateado
```

---

## 5. La base de datos explicada

### ¿Qué base de datos usamos?

**PostgreSQL 16** — la base de datos relacional de código abierto más potente. Usamos también la extensión **pgvector** que añade soporte para vectores (para búsqueda semántica futura).

### Tablas y para qué sirven

```
┌─────────────────────────────────────────────────────────┐
│  vehicles (44 filas)                                    │
│  ─────────────────────────────────────────────────────  │
│  vin (PK)   model        year   color   km              │
│  ─────────  ───────────  ─────  ──────  ─────           │
│  AK550-...  AK550 2023   2023   Rojo    1200            │
│  XCT400-..  Xciting 400  2022   Azul    3400            │
│                                                         │
│  → Identifica el vehículo cuando el técnico da el VIN  │
└────────────────────────┬────────────────────────────────┘
                         │ 1 vehículo → muchas sesiones
                         ▼
┌─────────────────────────────────────────────────────────┐
│  sessions (se crea una por cada conversación)           │
│  ─────────────────────────────────────────────────────  │
│  session_id (UUID)  vin  model  entry_point             │
│  status  started_at  ended_at  total_steps              │
│  final_result  success                                  │
│                                                         │
│  entry_point → por qué síntoma entró (symptom_motor...) │
│  final_result → diagnóstico dado ("Inyector defectuoso")│
│  status → 'active' mientras dura, 'closed' al terminar  │
└──┬──────────────────────────────┬───────────────────────┘
   │ 1 sesión → 1 estado          │ 1 sesión → muchos mensajes
   ▼                              ▼
┌─────────────────────┐   ┌──────────────────────────────┐
│  session_state      │   │  messages                    │
│  ─────────────────  │   │  ──────────────────────────  │
│  session_id (PK)    │   │  message_id (PK, autonum)    │
│  current_node       │   │  session_id                  │
│  current_symptom    │   │  role ('user'|'assistant')   │
│  state_json (JSONB) │   │  content                     │
│                     │   │  created_at                  │
│  → Dónde estamos    │   │                              │
│    en el árbol DDT  │   │  → Toda la conversación      │
│    ahora mismo      │   │    guardada mensaje a mensaje │
└─────────────────────┘   └──────────────────────────────┘
   │ 1 sesión → muchos logs          │ 1 sesión → 1 feedback
   ▼                                 ▼
┌─────────────────────┐   ┌──────────────────────────────┐
│  decision_logs      │   │  feedback                    │
│  ─────────────────  │   │  ──────────────────────────  │
│  log_id             │   │  feedback_id                 │
│  session_id         │   │  session_id                  │
│  module_name        │   │  useful (true/false)         │
│  input_summary      │   │  comment (texto)             │
│  output_summary     │   │  created_at                  │
│  created_at         │   │                              │
│                     │   │  → ¿Fue útil el diagnóstico? │
│  → Trazabilidad:    │   │                              │
│    qué módulo tomó  │   └──────────────────────────────┘
│    cada decisión    │
└─────────────────────┘

Tablas de CONOCIMIENTO (estáticas, se cargan una vez):

┌─────────────────────┐   ┌──────────────────────────────┐
│  diagnostic_trees   │   │  tree_nodes                  │
│  ─────────────────  │   │  ──────────────────────────  │
│  tree_id (PK)       │◄──│  tree_id (FK)                │
│  model              │   │  node_id                     │
│  symptom            │   │  node_type (question/diag)   │
│  version            │   │  content                     │
│  is_active          │   │  yes_next                    │
│                     │   │  no_next                     │
│  → Los 5 árboles    │   │                              │
│    DDT disponibles  │   │  → Cada pregunta/diagnóstico │
└─────────────────────┘   └──────────────────────────────┘

┌─────────────────────┐   ┌──────────────────────────────┐
│  faqs (40 filas)    │   │  historical_cases (76 filas) │
│  ─────────────────  │   │  ──────────────────────────  │
│  faq_id             │   │  case_id (CASE-001...)       │
│  question           │   │  model                       │
│  answer             │   │  symptom_category            │
│  category           │   │  case_text                   │
│  model              │   │  final_diagnosis             │
│  usage_count        │   │  base_confidence             │
│                     │   │                              │
│  → Ruta B: responde │   │  → Ruta C: busca casos       │
│    preguntas rápidas│   │    similares al texto libre  │
└─────────────────────┘   └──────────────────────────────┘
```

### Diagrama ER resumido

```
vehicles ──< sessions >── session_state
                 │
                 ├──< messages
                 ├──< decision_logs
                 └──1  feedback

diagnostic_trees ──< tree_nodes
faqs
historical_cases
```

### El campo `state_json` (JSONB) — la memoria de la sesión

Es el campo más importante para entender el sistema. Guarda el estado completo del grafo LangGraph en formato JSON:

```json
{
  "session_id": "uuid-...",
  "vin": "AK550-2023-001",
  "model": "AK550 2023",
  "current_symptom": "symptom_motor",
  "current_node": "q3",
  "tree_id": "AK550_MOTOR_V1",
  "messages": [...],
  "facts": {"humo_negro": false},
  "active_hypotheses": ["Inyector", "EGR"]
}
```

Entre mensaje y mensaje, el grafo **pausa** y guarda este estado. Al llegar el siguiente mensaje, lo recarga y continúa desde donde estaba.

---

## 6. Arquitectura del sistema

### Los tres servicios (contenedores Docker)

```
┌─────────────────────────────────────────────────────────────────┐
│                    MÁQUINA LOCAL / SERVIDOR                      │
│                                                                  │
│  ┌──────────────────┐    ┌─────────────────────┐                │
│  │   poc-frontend   │    │    poc-backend       │                │
│  │                  │    │                      │                │
│  │  React + Vite    │───►│  FastAPI + Python    │               │
│  │  Tailwind CSS    │    │  LangGraph           │                │
│  │                  │◄───│  Módulos de lógica   │               │
│  │  Puerto 3000     │    │  Puerto 8000         │                │
│  └──────────────────┘    └──────────┬───────────┘               │
│                                     │                            │
│                          ┌──────────▼───────────┐               │
│                          │    poc-postgres       │               │
│                          │                       │               │
│                          │  PostgreSQL 16        │               │
│                          │  + pgvector           │               │
│                          │  Puerto 5432          │               │
│                          └───────────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                                     │
                          ┌──────────▼───────────┐
                          │    GROQ API (nube)    │
                          │  llama-3.1-8b-instant │
                          │  Solo para Ruta C     │
                          └───────────────────────┘
```

### Cómo fluye una petición

```
1. Técnico escribe en el navegador
        │
        ▼
2. React (frontend) hace fetch() al backend
   POST http://localhost:8000/session/message
        │
        ▼
3. FastAPI recibe la petición
   Valida con Pydantic
   Llama a LangGraph
        │
        ▼
4. LangGraph ejecuta el grafo
   Consulta PostgreSQL (session_state, vehicles, tree_nodes...)
   Si es Ruta C → llama a Groq API
        │
        ▼
5. LangGraph devuelve el estado actualizado
   FastAPI construye la respuesta JSON
        │
        ▼
6. React recibe el JSON
   Renderiza el mensaje, menú o diagnóstico
   Actualiza la pantalla
```

### Estructura de carpetas (lo que existe realmente)

```
poc-asistente-tecnico/
│
├── docker-compose.yml          ← Orquesta los 3 contenedores
├── .env                        ← Claves y config (no se sube a Git)
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt        ← Dependencias Python
│   ├── main.py                 ← Entry point FastAPI, registra rutas
│   ├── core/
│   │   ├── config.py           ← Lee variables de entorno (.env)
│   │   ├── database.py         ← Engine async de SQLAlchemy
│   │   └── exceptions.py       ← Excepciones de dominio
│   ├── models/                 ← Clases ORM (cada tabla = una clase)
│   │   ├── session.py          ← Session, SessionState
│   │   ├── message.py          ← Message
│   │   ├── vehicle.py          ← Vehicle
│   │   ├── knowledge.py        ← FAQ, HistoricalCase, DiagnosticTree, TreeNode
│   │   ├── feedback.py         ← Feedback
│   │   └── decision_log.py     ← DecisionLog
│   ├── api/
│   │   ├── routes/
│   │   │   ├── session.py      ← POST /start, POST /message, GET /{id}, POST /feedback
│   │   │   ├── metrics.py      ← GET /metrics/summary
│   │   │   ├── analytics.py    ← GET /analytics/sessions|diagnoses|feedback|heatmap
│   │   │   └── knowledge.py    ← GET /knowledge/faqs|cases|trees
│   │   └── schemas/
│   │       └── session.py      ← Pydantic: request/response shapes
│   ├── modules/
│   │   ├── orchestrator/
│   │   │   ├── graph.py        ← Define el StateGraph de LangGraph
│   │   │   └── state.py        ← ConversationState (TypedDict)
│   │   ├── vin_lookup/         ← Consulta tabla vehicles
│   │   ├── tree_engine/        ← Navega árbol DDT nodo a nodo
│   │   ├── faq_matcher/        ← Busca en FAQs
│   │   ├── free_text_parser/   ← Analiza texto libre
│   │   ├── response_builder/   ← Formatea DiagnosisData
│   │   ├── session_state/      ← Lee/escribe state_json en BD
│   │   ├── historical_retrieval/ ← Busca casos históricos
│   │   └── traceability/       ← Escribe decision_logs
│   ├── services/
│   │   ├── tracing.py          ← save_message(), increment_steps(), log_decision()
│   │   └── tree_engine.py      ← Wrapper de acceso al árbol desde BD
│   └── db/
│       ├── migrations/init.sql ← DDL: crea todas las tablas
│       └── seeds/              ← SQL de datos de prueba
│           ├── vehicles.sql
│           ├── faqs.sql
│           ├── diagnostic_trees.sql
│           ├── historical_cases.sql
│           ├── consumo_tree.sql
│           ├── vehicles_enrichment.sql  ← 29 VINs más
│           ├── historical_cases_enrichment.sql
│           └── faqs_enrichment.sql
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── App.jsx             ← Layout raíz: header + sidebar + chat
│       ├── index.css           ← Tailwind + animaciones + scrollbar
│       ├── main.jsx            ← Monta <App/> en el DOM
│       ├── services/
│       │   └── api.js          ← Todas las llamadas fetch al backend
│       └── components/
│           ├── Chat/
│           │   ├── ChatContainer.jsx   ← Orquestador: sesión, mensajes, routing
│           │   ├── MessageBubble.jsx   ← Burbuja de mensaje individual
│           │   ├── InputBar.jsx        ← Campo de texto + botón enviar
│           │   ├── MenuOptions.jsx     ← Tarjetas de síntomas con emojis
│           │   ├── QuickReplies.jsx    ← Botones Sí/No y acciones rápidas
│           │   ├── DiagnosisResult.jsx ← Card del diagnóstico final
│           │   ├── RouteHeader.jsx     ← Cabecera al cambiar de ruta
│           │   └── ReconductionCard.jsx← Sugerencia de pasar a Ruta A
│           ├── UI/
│           │   ├── SessionSummaryPanel.jsx ← Modal resumen de sesión
│           │   ├── HealthIndicator.jsx     ← Puntito verde/rojo del backend
│           │   ├── PhaseBar.jsx            ← Barra de progreso del árbol
│           │   └── TreeProgressBar.jsx     ← Barra visual de nodo actual
│           └── Analytics/
│               ├── LeftNavSidebar.jsx  ← Sidebar izq. con 7 secciones acordeón
│               ├── SymptomHeatMap.jsx  ← Mapa de calor síntomas × modelos
│               └── PdfExport.jsx       ← Generador de informe PDF
│
└── docs/
    ├── DDT.md                  ← Documento de Diseño Técnico original
    ├── GUIA_DEMO.md            ← Guía completa para demos
    ├── TECHNICAL_SPEC.md       ← Especificación técnica de todos los archivos
    ├── FUNCTIONAL_OVERVIEW.md  ← Visión funcional para no técnicos
    └── diagrams/
        ├── database-er.mmd     ← Diagrama ER en Mermaid
        └── flujo-asistente.mmd ← Flujo del asistente en Mermaid
```

---

## 7. Tecnologías: qué son, cómo funcionan y por qué las usamos

---

### LangGraph

#### ¿Qué es?
LangGraph es una librería de Python de la familia LangChain que permite definir **flujos conversacionales como un grafo de estados**. En vez de tener el código del chatbot como una secuencia lineal de `if/else`, lo defines como un grafo dirigido donde cada nodo es una función.

#### ¿Cómo funciona internamente?

```python
# Defines un grafo con estado compartido
graph = StateGraph(ConversationState)

# Añades nodos (cada uno es una función Python)
graph.add_node("dispatch", dispatch_fn)
graph.add_node("vin_lookup", vin_lookup_fn)
graph.add_node("tree_engine", tree_engine_fn)

# Añades aristas (condiciones de transición)
graph.add_conditional_edges("dispatch", decide_next, {
    "has_vin": "show_menu",
    "no_vin": "request_vin"
})

# Compilas y ejecutas
app = graph.compile()
result = app.invoke(state, config={"entry_point": "dispatch"})
```

El grafo puede **pausar** entre mensajes. Cuando el usuario responde, se reanuda exactamente donde se paró. Esto es lo que permite navegar el árbol DDT a lo largo de varios mensajes.

#### ¿Por qué LangGraph y no otra cosa?

| Alternativa | Problema |
|---|---|
| `if/else` puro | Se vuelve inmanejable con muchas rutas |
| LangChain Chains | No maneja bien la pausa/reanudación entre mensajes |
| Rasa / DialogFlow | Overkill para POC, más difícil de personalizar |
| **LangGraph** | Grafo explícito, pausable, trazable, Pythónico ✓ |

**Versión usada**: `langgraph==0.2.28`

---

### LLM / Groq

#### ¿Qué es un LLM?
Un **LLM (Large Language Model)** es un modelo de IA entrenado con enormes cantidades de texto que puede entender y generar texto en lenguaje natural. ChatGPT es el más conocido.

#### ¿Qué es Groq?
Groq es una empresa que ofrece **inferencia ultra-rápida** de LLMs de código abierto (como Llama de Meta). Su ventaja es la velocidad: responde en < 1 segundo frente a los 5-10 segundos de otros proveedores.

Ofrecen un **tier gratuito** generoso para desarrollo y POC.

#### ¿Qué modelo usamos?
`llama-3.1-8b-instant` — versión de 8 billones de parámetros de Llama 3.1, optimizada para velocidad. Es suficiente para el análisis de texto libre y síntesis de diagnósticos.

#### ¿Para qué lo usamos exactamente?
Solo en la **Ruta C (texto libre)**:
1. El técnico describe: "La moto tiembla mucho al frenar cuesta abajo"
2. El sistema recupera casos históricos similares
3. Llama al LLM con el contexto: "Dado estos casos similares: [...], ¿cuál es el diagnóstico más probable?"
4. El LLM sintetiza la respuesta

#### ¿Por qué NO usamos el LLM para todo?
- **Coste**: cada llamada consume tokens (= dinero)
- **Latencia**: añade 0.5-2 segundos al tiempo de respuesta
- **Alucinaciones**: el LLM puede inventar diagnósticos técnicos incorrectos
- **Sin control**: no se puede auditar qué "razonó" el LLM
- El árbol DDT es **determinista** — mismo síntoma, mismo resultado, sin variabilidad

---

### FastAPI

#### ¿Qué es?
Framework web de Python para construir APIs REST. Es moderno (basado en Python 3.10+ con tipos), ultra-rápido (usa ASGI/asyncio) y genera documentación automática en `/docs`.

#### ¿Por qué FastAPI y no Flask/Django?

| | FastAPI | Flask | Django |
|---|---|---|---|
| Velocidad | ⚡ Async nativo | Sync (más lento) | Sync |
| Tipado | ✓ Automático | Manual | Manual |
| Documentación | ✓ Auto (Swagger) | Manual | Parcial |
| Validación | ✓ Pydantic | Manual | Formularios |
| Para POC/API | ✓ Ideal | Sí, más simple | Overkill |

**Versión**: `fastapi==0.115.2`

#### Pydantic — el sistema de validación

Pydantic es la librería que usa FastAPI para validar datos de entrada y salida. Cuando el frontend envía `{ session_id: "abc", message: "Sí" }`, Pydantic verifica automáticamente que los tipos son correctos antes de que el código se ejecute.

```python
class MessageRequest(BaseModel):
    session_id: str = Field(..., description="UUID de la sesión")
    message: str = Field(..., min_length=1, max_length=2000)
    # Si falta session_id o el message está vacío → error 422 automático
```

---

### PostgreSQL + pgvector

#### ¿Qué es PostgreSQL?
La base de datos relacional de código abierto más avanzada del mundo. Guarda datos en tablas con filas y columnas, con relaciones entre ellas (las FK que vimos en el ER). Lleva más de 30 años de desarrollo.

#### ¿Por qué PostgreSQL y no MySQL, SQLite, MongoDB?

| | PostgreSQL | MySQL | SQLite | MongoDB |
|---|---|---|---|---|
| JSONB nativo | ✓ | Limitado | No | ✓ (es NoSQL) |
| pgvector | ✓ | No | No | No |
| Relaciones FK | ✓ | ✓ | ✓ | No (NoSQL) |
| Para POC→Prod | ✓ | ✓ | Solo POC | Diferente paradigma |

Necesitamos JSONB para el `state_json` (estado del grafo) y pgvector para búsqueda semántica futura.

#### ¿Qué es pgvector?
Es una extensión de PostgreSQL que añade el tipo de dato `VECTOR` y operadores de similitud. Un vector es una lista de números (embedding) que representa el "significado" de un texto en un espacio matemático.

**Estado actual en POC**: pgvector está instalado pero los embeddings no se generan (el endpoint de Groq para embeddings devuelve 404 con el plan gratuito). La búsqueda lexical (búsqueda de palabras) se usa como fallback. En producción se activaría con un proveedor de embeddings real.

#### SQLAlchemy — el ORM
SQLAlchemy es la capa entre Python y PostgreSQL. En vez de escribir SQL directamente, trabajas con clases Python:

```python
# Sin ORM (SQL directo):
await db.execute("SELECT * FROM sessions WHERE session_id = $1", [session_id])

# Con SQLAlchemy ORM:
result = await db.execute(select(Session).where(Session.session_id == session_uuid))
session = result.scalar_one_or_none()
# Ahora tienes un objeto Python: session.vin, session.model, etc.
```

**Versión async**: Usamos `AsyncSession` y `create_async_engine` para que las consultas no bloqueen el servidor (importante en FastAPI que es async).

---

### React + Vite + Tailwind

#### React
Librería JavaScript para construir interfaces de usuario. La UI se divide en **componentes** (piezas reutilizables). Cuando el estado cambia (ej. llega un mensaje nuevo), React actualiza automáticamente solo las partes de la pantalla que cambiaron.

```jsx
// Un componente React = una función que devuelve HTML (JSX)
function MessageBubble({ role, content }) {
  return (
    <div className={role === 'user' ? 'text-right' : 'text-left'}>
      {content}
    </div>
  )
}
```

**Por qué React**: Es el framework más usado del mercado, con el ecosistema más grande. Cualquier desarrollador frontend lo conoce.

#### Vite
El "bundler" o empaquetador. Convierte los archivos JSX, CSS e imágenes en HTML/JS/CSS que el navegador puede entender. Es 10-20x más rápido que el antiguo Webpack.

En producción, `npm run build` genera la carpeta `dist/` con los archivos optimizados que sirve Docker.

#### Tailwind CSS
Framework de estilos "utility-first". En vez de escribir CSS en archivos separados, añades clases directamente en el HTML:

```jsx
// Sin Tailwind (CSS separado):
// .chat-bubble { background: #1f2937; border-radius: 12px; padding: 12px; }
<div className="chat-bubble">...</div>

// Con Tailwind (todo inline):
<div className="bg-gray-800 rounded-xl p-3">...</div>
```

El tema oscuro del chat se construyó con clases como `bg-gray-950`, `text-gray-100`, `border-gray-800`.

---

### Docker

#### ¿Qué es?
Docker empaqueta cada servicio (backend, frontend, BD) en un **contenedor** aislado. Un contenedor es como una "mini-máquina virtual" que incluye todo lo necesario para ejecutar el servicio: sistema operativo mínimo, Python/Node, dependencias, código.

#### ¿Por qué Docker?
- **"Funciona en cualquier máquina"**: mismo resultado en tu portátil, en el servidor del cliente o en la nube
- **Aislamiento**: el backend no interfiere con el frontend aunque usen versiones distintas de Python/Node
- **Un solo comando**: `docker compose up --build` levanta todo el sistema

#### Docker Compose
Archivo `docker-compose.yml` que define los 3 contenedores y cómo se conectan:

```yaml
services:
  postgres:    ← BD siempre se levanta primero (healthcheck)
    image: pgvector/pgvector:pg16
    
  backend:     ← Espera a que postgres esté sano
    depends_on:
      postgres:
        condition: service_healthy

  frontend:    ← Espera a que backend esté levantado
    depends_on:
      - backend
```

---

## 8. Panel de analítica

El sidebar izquierdo (siempre visible, colapsable) tiene 7 secciones:

| Sección | Datos que muestra | Endpoint |
|---|---|---|
| 📊 Métricas | Sesiones totales, tasa éxito, módulos, top diagnósticos | `/metrics/summary` |
| 🗂️ Sesiones | Últimas sesiones con modelo, estado, diagnóstico | `/analytics/sessions` |
| 🔎 Diagnósticos | Ranking de diagnósticos más frecuentes + barras | `/analytics/diagnoses` |
| 💬 Feedback | Resumen 👍/👎 + comentarios de técnicos | `/analytics/feedback` |
| 📚 Conocimiento | Árboles DDT / FAQs / Casos históricos | `/knowledge/faqs|cases|trees` |
| 🌡️ Mapa de calor | Grid modelos × síntomas coloreado por frecuencia | `/analytics/heatmap` |
| 📄 Exportar PDF | Informe completo con KPIs + tablas → diálogo imprimir | múltiples |

### ¿Cómo funciona el mapa de calor?

El backend combina dos fuentes de datos:
1. Tabla `sessions` → qué síntoma (entry_point) usó cada sesión y en qué modelo
2. Tabla `historical_cases` → cuántos casos hay por modelo y symptom_category

Los combina en una matriz y devuelve:
```json
{
  "models": ["AK550 2023", "Xciting 400", ...],
  "symptoms": ["Paradas de motor", "Arranque", ...],
  "rows": [
    { "symptom": "Paradas de motor", "AK550 2023": 15, "Xciting 400": 5 },
    ...
  ],
  "max_value": 15
}
```

El frontend colorea cada celda: verde (bajo) → amarillo → naranja → rojo (crítico).

---

## 9. Preguntas que puede hacer tu jefe

**"¿Por qué no usáis ChatGPT directamente?"**
Porque el árbol DDT es determinista — ChatGPT puede alucinar (inventar diagnósticos). El árbol siempre da el mismo resultado para la misma secuencia de respuestas, que es lo que necesita un protocolo técnico oficial. Usamos IA solo cuando el técnico describe algo que no encaja en ningún árbol.

**"¿Qué pasa si el técnico no sabe el bastidor?"**
El sistema no permite continuar sin VIN válido. Tras 3 intentos fallidos, cierra la sesión en error. Esto es una regla de negocio fundamental: el modelo del vehículo debe ser conocido antes de diagnosticar.

**"¿Cómo de seguro es?"**
En POC no hay autenticación. Para producción se añadiría login (JWT/OAuth2), HTTPS y los VINs vendrían del sistema real del fabricante. La BD ya tiene trazabilidad completa de todo lo que ocurre.

**"¿Cuánto cuesta el LLM?"**
Groq tiene un tier gratuito de 6.000 requests/día. En producción, con un modelo Llama local, el coste sería cero (hardware propio). Con Groq de pago, ~$0.05 por 1M tokens ≈ fracciones de céntimo por diagnóstico.

**"¿Se puede añadir un modelo nuevo de moto?"**
Sí: (1) insertar VINs en `vehicles`, (2) crear el árbol DDT en `diagnostic_trees` + `tree_nodes`, (3) añadir casos históricos en `historical_cases`. El sistema lo detecta automáticamente.

**"¿Cuánto tiempo lleváis desarrollando esto?"**
La POC completa (desde cero) se desarrolló en 5 sesiones de trabajo. La arquitectura modular y las tecnologías elegidas permitieron avanzar muy rápido sin deuda técnica.

**"¿Es escalable?"**
La arquitectura permite:
- Añadir modelos de moto: solo SQL
- Añadir síntomas: nuevos árboles DDT
- Añadir FAQs: más filas en la tabla
- Escalar a más usuarios: Docker → Kubernetes, PostgreSQL → servicio gestionado
- Añadir embeddings semánticos: pgvector ya instalado, solo falta el proveedor
- Separar servicios: cada módulo es independiente y puede extraerse

---

*Documento de estudio — POC Asistente Técnico · Mayo 2025*

---

# 10. Auditoría técnica del código — Lo que debes saber si te preguntan

> Esta sección documenta los hallazgos reales del código tal como está implementado.
> Cosas que pueden preguntarte en una revisión o entrevista técnica.

## 10.1 Cómo funciona `_is_tree_node` — y por qué importa

El sistema necesita saber, turno a turno, si estamos **en medio de un árbol de diagnóstico** o no. Esto lo resuelve la función `_is_tree_node` en `api/routes/session.py`:

```python
def _is_tree_node(node: str | None) -> bool:
    if not node:
        return False
    return len(node) <= 5 and (node[0] in ("n", "c", "a", "x", "q")) and node[1:].isdigit()
```

**Convención de IDs de nodo por árbol:**

| Árbol | Prefijo | Ejemplos |
|---|---|---|
| AK550_MOTOR_V1 | `n` | n1, n2, n3 … n9 |
| AK550_CELP_V1 | `c` | c1, c2, c3, c4, c5 |
| AK550_ARRANQUE_V1 | `a` | a1, a2 … a13 |
| XCITING_MOTOR_V1 | `x` | x1, x2 … |
| AK550_CONSUMO_V1 | `q` | q1, q2 … q13 |

**Flujo de persistencia mid-tree:**
1. `tree_engine_node` llama `_persist_tree_state(db, session_id, node_id, state_json)` → guarda el nodo actual ("n3") en `session_state.current_node`
2. En el siguiente turno, `_determine_entry_node` lee `session_state.current_node`, detecta que es un tree node → devuelve `"tree_engine"` como entry del grafo
3. `graph_state["tree_node"] = session_state.current_node` → el tree_engine sabe desde qué nodo continuar

**Si añades un árbol nuevo, el prefijo del ID de nodo DEBE ser una letra de la lista `("n", "c", "a", "x", "q")` y seguido SOLO de dígitos. Si no, el sistema no detectará que estamos mid-tree y perderá el estado.**

## 10.2 La función `route_from_dispatch` — cómo el grafo sabe dónde continuar

```python
def route_from_dispatch(state):
    node = state.get("current_node", "vin_lookup")
    if node == "tree_engine":      return "tree_engine"
    if node == "classifier_node":  return "classifier_node"
    if node == "show_menu":        return "show_menu"
    return "vin_lookup"
```

El API construye `graph_state["current_node"]` con el valor de `_determine_entry_node()` antes de llamar al grafo. Esto hace que `dispatch_node` sea un nodo **vacío** (solo pasa el estado) y toda la lógica de enrutamiento vive fuera del grafo — en el API layer. Es una decisión de diseño deliberada para mantener el grafo limpio y testeable.

## 10.3 El contrato de salida estándar del diagnóstico

Toda ruta (A, B o C) devuelve el mismo formato:

```python
{
    "primary_hypothesis": "Sensor de inclinación defectuoso",
    "alternatives": ["Bomba de gasolina defectuosa", "Agua en el depósito"],
    "next_check": "Comprobar sensor de inclinación con multímetro",
    "short_explanation": "El síntoma sugiere...",
    "confidence": 0.90,       # fijo 0.90 en árbol; variable en Ruta C
    "source_type": "tree"     # "tree" | "faq" | "historical"
}
```

- **Ruta A (árbol)**: `confidence = 0.90` siempre (resultado determinista, sin incertidumbre)
- **Ruta C (histórico)**: `confidence` viene del ranking híbrido (score ponderado)

## 10.4 El ranking híbrido de la Ruta C

```
score = 0.4 × semantic_similarity
      + 0.3 × model_match_bonus
      + 0.2 × base_confidence
      + 0.1 × frequency_score
```

- **semantic_similarity**: similitud coseno entre el embedding del texto del usuario y el embedding del caso histórico. Si Groq embeddings no están disponibles (el modelo fue retirado), usa fallback léxico (solapamiento de palabras TF-IDF simplificado).
- **model_match_bonus**: 1.0 si el modelo del vehículo coincide, 0.0 si no.
- **base_confidence**: campo `base_confidence` del caso en BD (0.0-1.0, asignado manualmente en el seed).
- **frequency_score**: normalización logarítmica del número de casos del mismo tipo.

**¿Por qué 0.4 para semántica?** Porque es el criterio más relevante pero no absoluto — el modelo del vehículo también es crítico (0.3).

## 10.5 Groq embeddings — el fallback silencioso

El modelo de embeddings de Groq (`nomic-embed-text-v1_5`) **no está disponible** actualmente en la API (el endpoint devuelve 404). El código lo maneja:

```python
# En faq_matcher.py y free_text.py
try:
    query_embedding = await get_embedding(user_message)
except Exception:
    query_embedding = None  # Activa el fallback léxico
```

**Consecuencias:**
- FAQ Ruta B: usa búsqueda léxica (GIN index sobre `tsvector`) en lugar de similitud vectorial
- Ruta C: el campo `semantic_similarity` del ranking vuelve al fallback léxico
- La columna `embedding vector(768)` en `knowledge_chunks` existe pero está vacía (`NULL`)
- **El sistema funciona igual** — los resultados son algo menos precisos semánticamente

## 10.6 El bug `AK550_CONSUMO_V1` — diagnóstico y solución

**Síntoma**: si el usuario selecciona "Consumo excesivo" en el menú (solo visible en AK550), el sistema responde "Error: árbol de diagnóstico 'AK550_CONSUMO_V1' no disponible."

**Causa**: `consumo_tree.sql` no estaba montado en `docker-compose.yml` como volumen de inicialización de PostgreSQL. Docker solo carga los archivos de `/docker-entrypoint-initdb.d/` cuando el volumen está **vacío** (primera vez). Si el volumen ya existe, los seeds NO se recargan.

**Solución aplicada**: se añadieron al `docker-compose.yml`:
```yaml
- ./backend/db/seeds/consumo_tree.sql:/docker-entrypoint-initdb.d/07_consumo_tree.sql
- ./backend/db/seeds/vehicles_enrichment.sql:/docker-entrypoint-initdb.d/08_vehicles_enrichment.sql
- ./backend/db/seeds/faqs_enrichment.sql:/docker-entrypoint-initdb.d/09_faqs_enrichment.sql
- ./backend/db/seeds/historical_cases_enrichment.sql:/docker-entrypoint-initdb.d/10_cases_enrichment.sql
```

**Para aplicar en BD existente** (el volumen ya existe):
```bash
# Opción A: reset completo (borra datos existentes)
docker compose down -v
docker compose up --build

# Opción B: carga manual sin borrar datos
docker exec -i poc-postgres psql -U poc_user -d poc_asistente < backend/db/seeds/consumo_tree.sql
docker exec -i poc-postgres psql -U poc_user -d poc_asistente < backend/db/seeds/vehicles_enrichment.sql
```

## 10.7 Cómo funciona `session.entry_point` — vs síntoma real

`entry_point` se guarda en `sessions` la primera vez que el usuario elige una ruta:

```python
if not session.entry_point and result_state.get("route"):
    session.entry_point = result_state["route"]
```

`route` puede ser: `"tree"`, `"faq"`, `"other"`.

**Esto NO guarda el síntoma específico** (ej. "symptom_motor"). El síntoma específico se guarda en `session_state.current_symptom`. Para el heatmap de analítica, el endpoint combina:
- `Session.entry_point` (para sesiones reales) → pasa por `_SYMPTOM_LABELS` → "Árbol DDT (genérico)" o "Consulta FAQ"
- `HistoricalCase.symptom_category` (para casos de conocimiento) → pasa por `_SYMPTOM_LABELS` → "Paradas de motor", "Testigo CELP", etc.

## 10.8 Tabla de módulos vs secciones del DDT

| Módulo en código | Sección DDT | Responsabilidad |
|---|---|---|
| `orchestrator/graph.py` | §6, §15 | StateGraph, nodos, edges condicionales |
| `orchestrator/nodes/vin_lookup.py` | §16, RN-NEG-001,002,009 | Lookup de bastidor, max 3 intentos |
| `orchestrator/nodes/menu.py` | §17 | Menú dinámico por modelo |
| `orchestrator/nodes/classifier.py` | §18 | Clasificación de intención (A/B/C) |
| `orchestrator/nodes/tree_engine.py` | §19, §12 | Motor de árbol + hipótesis activas |
| `orchestrator/nodes/faq_matcher.py` | §20 | Búsqueda semántica/léxica en FAQs |
| `orchestrator/nodes/free_text.py` | §21 | Texto libre + tags LLM + ranking |
| `services/response_builder.py` | §22 | Contrato de salida estándar |
| `services/ranking.py` | §21 | Ranking híbrido (4 componentes) |
| `services/tracing.py` | §14 | Trazabilidad: decision_logs + messages |
| `api/routes/session.py` | §13 | Endpoints REST + reconstrucción de estado |
| `db/migrations/init.sql` | §23 | DDL completo con pgvector + índices |

## 10.9 El estado conversacional — fuente de verdad

```
┌──────────────────────────────────────────────────────────┐
│                  ConversationState (TypedDict)           │
│                                                          │
│  session_id, vin, model              ← identidad        │
│  current_node                        ← posición en grafo│
│  tree_node, tree_id                  ← posición en árbol│
│  user_message, assistant_message     ← turno actual     │
│  message_type                        ← contrato frontend│
│  options                             ← quick replies    │
│  state_json                          ← todo lo demás    │
│    ├── asked_questions []            ← historial árbol  │
│    ├── facts {}                      ← respuestas dadas │
│    ├── active_hypotheses []          ← hipótesis vivas  │
│    ├── current_symptom               ← síntoma elegido  │
│    ├── awaiting_input                ← ruta B/C pendiente│
│    ├── tree_id                       ← árbol activo     │
│    └── vin_attempts                  ← contador intentos│
│  vin_attempts                        ← también top-level│
│  route                               ← "tree"|"faq"|... │
│  diagnosis_result                    ← resultado final  │
│  step_number                         ← progreso árbol   │
└──────────────────────────────────────────────────────────┘
```

`state_json` es el "maletín" que viaja entre turnos persistido en `session_state.state_json` (JSONB). Todo lo que el árbol necesita recordar entre preguntas vive ahí.

## 10.10 Preguntas frecuentes de entrevista técnica sobre el DDT

**"¿Por qué no se usa el LLM como memoria de la conversación?"**
El LLM no es la memoria — el estado en PostgreSQL lo es. El LLM solo se usa para: (1) extraer tags del texto libre, (2) clasificar intención, (3) redactar respuestas. El estado es determinista y auditáble.

**"¿Qué pasa si el LLM falla?"**
- En clasificación: fallback a `"route": "other"` (Ruta C libre)
- En extracción de tags: devuelve `{}` y el ranking usa solo similitud léxica
- En embeddings: fallback léxico para similitud semántica
- El sistema **nunca cae** por fallo del LLM — todas las funciones tienen try/except con fallback

**"¿Cómo se garantiza que el diagnóstico viene del vehículo correcto?"**
El modelo se obtiene de `vehicles.model` cuando se valida el VIN — nunca del texto del usuario (RN-NEG-002). Todo el filtrado de históricos, árboles y FAQs usa `session.model` que viene de la BD.

**"¿Cómo funciona el hipótesis tracking del árbol?"**
`_compute_active_hypotheses` hace un BFS desde el nodo actual y cuenta cuántos nodos `"type": "diagnosis"` son aún alcanzables. El score es `1/N` donde N es el número de diagnósticos aún posibles. Así el score sube conforme se eliminan hipótesis (las preguntas Sí/No van descartando ramas del árbol).

**"¿Por qué LangGraph en lugar de una máquina de estados simple?"**
LangGraph facilita: nodos async, estados TypedDict tipados, edges condicionales legibles, y preparación para añadir checkpointing (memoria de sesión larga) sin cambiar la arquitectura.

