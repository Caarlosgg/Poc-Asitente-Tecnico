# POC — Asistente Técnico de Diagnóstico

Sistema conversacional para técnicos de taller que guía el diagnóstico de motocicletas mediante árboles de decisión estructurados (DDT), base de FAQs e IA generativa. El técnico identifica la moto por bastidor (VIN) y el asistente le lleva hasta un diagnóstico concreto.

**Stack:** React 18 · FastAPI · LangGraph · PostgreSQL 16 + pgvector · Groq API (llama-3.1-8b-instant) · Docker

---

## Inicio rápido

### Prerrequisitos
- Docker + Docker Compose instalados
- Clave API de Groq → [console.groq.com](https://console.groq.com)

### 1. Clonar y configurar entorno

```bash
git clone <repo>
cd poc-asistente-tecnico
cp .env.example .env
# Editar .env → añadir GROQ_API_KEY=gsk_...
```

### 2. Levantar todo con un comando

```bash
docker compose up --build
```

> Primera vez tarda ~2-3 min (build de imágenes + carga de seeds SQL).

| Servicio | URL |
|---|---|
| Chat (frontend) | http://localhost:3000 |
| API (backend) | http://localhost:8000 |
| Swagger / Docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

### 3. Probar el flujo

1. Abre http://localhost:3000
2. El asistente pedirá el **bastidor (VIN)** — usa uno de los VINs de prueba:
   - `AK550-POC-0001` (AK550 — tiene árboles DDT completos)
   - `XCITING-POC-0001` (Xciting S 400)
   - `CV5-POC-0001` (CV5 — solo FAQ + texto libre)
3. Elige un síntoma del menú y sigue el flujo guiado

> **VINs de prueba recomendados:**
> - `AK550-POC-0001` → AK550 con árboles DDT completos (Motor, Arranque, CELP, Consumo)
> - `XCITING-POC-0001` → Xciting S 400 con árbol de Motor
> - `CV5-2023-0001` → CV5, solo Ruta B (FAQ) + Ruta C (IA libre)

---

## Cómo funciona — Flujo general del asistente

```mermaid
flowchart TD
    A([Usuario inicia conversación]) --> B{¿Sesión activa?}
    B -- SÍ --> C[Cargar contexto de sesión\nmodel · vin · state_json]
    B -- NO --> D[Asistente solicita bastidor VIN]
    C --> M
    D --> E[Usuario introduce VIN]
    E --> F{¿VIN existe en\ntabla vehicles?}
    F -- NO --> G[Error: VIN no encontrado\nMensaje claro al usuario]
    G --> H{¿Reintentos < 3?}
    H -- NO --> I([🚫 Fin — Límite alcanzado\nRN-NEG-009])
    H -- SÍ --> E
    F -- SÍ --> J[✅ Cargar contexto del modelo\nmodel · family · displacement_cc]
    J --> K[Crear sesión + session_state\nRegistrar en decision_logs]
    K --> M

    M[📋 Mostrar menú principal\nSíntomas · Consultas FAQ · Describir problema]
    M --> N[Usuario selecciona opción\no describe problema]
    N --> O[🤖 classifier_node — Groq\nExtrae intención y decide ruta]

    O --> PA[🌳 RUTA A — Árbol de Decisión DDT\nSíntoma crítico con árbol disponible]
    O --> PB[📚 RUTA B — FAQ Semántica\nConsulta técnica frecuente]
    O --> PC[🔍 RUTA C — Historial Híbrido\nEntrada libre sin árbol]

    PA --> PA1[Cargar tree_json desde\ntabla diagnostic_trees]
    PA1 --> PA2[Lanzar nodo inicial → Pregunta al usuario Sí/No]
    PA2 --> PA3[Usuario responde]
    PA3 --> PA4{¿Nodo siguiente?}
    PA4 -- Nueva pregunta --> PA2
    PA4 -- Fuera de alcance --> PA5[⚠️ Respuesta controlada\nRN-NEG-007]
    PA4 -- Diagnóstico final --> RB

    PB --> PB1[Generar embedding del texto\nnomic-embed-text-v1_5 vía Groq]
    PB1 --> PB2[Búsqueda similitud coseno pgvector\nen knowledge_chunks · filtro por model]
    PB2 --> PB3{¿Similitud ≥ 0.75?}
    PB3 -- SÍ --> PB4[Redactar respuesta RAG con LLM\nsource_type: faq · incrementa usage_count]
    PB3 -- NO --> PC
    PB4 --> RB

    PC --> PC1[Extraer tags con LLM\nGroq: síntoma · severidad · contexto]
    PC1 --> PC2[Generar embedding del texto\nnomic-embed-text-v1_5 vía Groq]
    PC2 --> PC3[Filtrar historical_cases por model\nRN-NEG-006]
    PC3 --> PC4[Ranking híbrido de candidatos\n0.4·semántica + 0.3·modelo + 0.2·confianza + 0.1·frecuencia]
    PC4 --> PC5[🏆 Top-3 hipótesis · Narrativa con LLM\nGroq: diagnóstico personalizado al técnico]
    PC5 --> PC6{¿Score top-candidato ≥ 0.72\ny síntoma con árbol disponible?}
    PC6 -- SÍ --> PC7[Sugerir reconducción a árbol DDT\nincluye suggests_tree en estado]
    PC6 -- NO --> RB
    PC7 --> RB

    RB[📄 Formatear salida uniforme\nresponse_builder → Contrato estándar]
    RB --> OUT[📦 Hipótesis principal + Alternativas\n+ Siguiente comprobación + Confianza 0-1]
    OUT --> TRACE[💾 Persistir trazabilidad\nINSERT messages · INSERT decision_logs · UPDATE session_state]
    TRACE --> CONT{¿Usuario quiere continuar?}
    CONT -- SÍ → Nueva consulta --> M
    CONT -- NO → Finalizar --> FB[Solicitar feedback\n¿Fue útil el diagnóstico?]
    FB --> FBS[💾 Guardar en tabla feedback\nUPDATE sessions: status=finished · success · final_result]
    FBS --> FIN([FIN])

    style PA  fill:#155724,color:#ffffff,stroke:#0a3015
    style PB  fill:#004085,color:#ffffff,stroke:#001f40
    style PC  fill:#7d4e00,color:#ffffff,stroke:#4d3000
    style RB  fill:#3d1a78,color:#ffffff,stroke:#280d57
    style I   fill:#721c24,color:#ffffff,stroke:#4a0d14
    style FIN fill:#0c5460,color:#ffffff,stroke:#062c33
```

---

## Arquitectura del sistema

```mermaid
flowchart TD
    subgraph FE["🖥 CAPA FRONTEND — React 18 · Puerto 3000"]
        UI["Interfaz de Chat\nBotones · Quick Replies · Menús"]
        SIDEBAR["Panel de Analítica\nMétricas · Sesiones · Diagnósticos\nFeedback · Conocimiento · Mapa de calor · PDF"]
    end

    subgraph BE["⚙️ CAPA BACKEND — Python + FastAPI · Puerto 8000"]
        ROUTER["API Router\n/session/start · /session/message\n/session/{id} · /metrics/summary\n/analytics/* · /knowledge/*"]
        ORCH["🔀 Orquestador — LangGraph\nStateGraph · ConversationState\nControl de estado conversacional"]
        VIN["🔍 vin_lookup_node\nValida VIN en tabla vehicles\nMáx. 3 intentos (RN-NEG-009)"]
        FAQ["📋 faq_matcher_node\nEmbedding + pgvector en knowledge_chunks\nUmbral similitud 0.75"]
        TREE["🌳 tree_engine_node\nNavega tree_json Sí/No\nMotor · Arranque · CELP · Consumo"]
        FREE["💬 free_text_node\nExtrae tags con LLM\nRanking híbrido en historical_cases"]
        TRACE["📝 Trazabilidad\ndecision_logs + messages"]
        RB["📄 response_builder\nContrato estándar de salida\nhipótesis · confianza · siguiente paso"]
    end

    subgraph DB["🗄 CAPA DE DATOS — PostgreSQL 16 + pgvector · Puerto 5432"]
        DBV["🚗 vehicles\nVIN · model · family · displacement_cc · market"]
        DBS["🔄 sessions + session_state\nEstado vivo de la sesión\ncurrent_node · tree_node · state_json"]
        DBM["💬 messages + decision_logs\nHistorial completo · Trazabilidad"]
        DBK["📚 faqs + diagnostic_trees\nFAQs curadas · Árboles DDT (tree_json JSONB)"]
        DBH["🔢 knowledge_chunks + historical_cases\nEmbeddings vector(768) · pgvector\nCasos históricos filtrados por model"]
        DBE["⚙️ embedding_jobs\nControl de generación de embeddings\nnomic-embed-text-v1_5"]
    end

    subgraph EXT["☁️ SERVICIOS EXTERNOS — IA"]
        LLM["🤖 Groq API\nllama-3.1-8b-instant · nomic-embed-text-v1_5\nClasificación · Embeddings · Narrativa\n(Rutas B y C)"]
    end

    USER(["👤 Usuario / Técnico"])

    USER -- "Texto / Selección" --> FE
    FE -- "REST / JSON" --> ROUTER
    ROUTER --> ORCH
    ORCH --> VIN
    ORCH --> TREE
    ORCH --> FAQ
    ORCH --> FREE
    ORCH --> RB
    ORCH --> TRACE

    VIN -- "Valida VIN" --> DBV
    ORCH -- "Lee / Escribe sesión" --> DBS
    TRACE -- "Registra trazas" --> DBM
    TREE -- "Carga árbol JSON" --> DBK
    FAQ -- "Búsqueda semántica pgvector" --> DBH
    FREE -- "Consulta históricos por model" --> DBH

    ORCH -- "Clasifica intención" --> LLM
    FAQ -- "Genera embedding + redacta respuesta" --> LLM
    FREE -- "Extrae tags + narrativa diagnóstica" --> LLM

    ROUTER -- "Feedback + Métricas\n/session/{id}/feedback · /metrics/summary" --> DBM

    style FE   fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    style BE   fill:#fef9c3,stroke:#d97706,color:#78350f
    style DB   fill:#dcfce7,stroke:#16a34a,color:#14532d
    style EXT  fill:#f3e8ff,stroke:#9333ea,color:#581c87
    style LLM  fill:#7c3aed,color:#ffffff,stroke:#6d28d9
    style USER fill:#1e40af,color:#ffffff,stroke:#1e3a8a
    style ORCH fill:#92400e,color:#ffffff,stroke:#78350f
```

---

## LangGraph — el grafo de conversación

```
[START]
    │
    ▼
[dispatch_node]
    │
    ├── sin VIN ──────────────────────► [vin_lookup_node]
    │                                         │
    │                               ┌─────────┴──────────┐
    │                          VIN válido           No válido
    │                               │           (máx 3 intentos)
    │                               ▼                    │
    │                        [show_menu_node]   [session_end_error_node]
    │                               │
    │              ┌────────────────┼────────────────┐
    │              ▼                ▼                ▼
    │        síntoma A           FAQ B           libre C
    │    [classifier_node]   ──► [faq_matcher]  [free_text_node]
    │            │               (Ruta B)       (Ruta C)
    │            │                  │
    │      ┌─────┴──────┐          │ no match → [free_text_node]
    │      ▼            ▼
    │ [tree_engine]  [await_input_node]
    │  (Ruta A)      (espera categ. FAQ)
    │      │
    │  pregunta Sí/No al usuario
    │      │◄───────────────────────┐
    │      │                        │
    │  (respuesta usuario)          │
    │      │                        │
    │  ¿diagnóstico? ── NO ─────────┘
    │      │
    │     SÍ
    │      ▼
    │  [END — end_with_diagnosis]
    │
    └─────► [END — end_with_answer / session_end_error]
```

---

## Base de datos — relaciones y schema completo

```mermaid
erDiagram
    VEHICLES ||--o{ SESSIONS : "vin"
    VEHICLES ||--o{ SESSION_STATE : "vin"
    SESSIONS ||--|| SESSION_STATE : "session_id"
    SESSIONS ||--o{ MESSAGES : "session_id"
    SESSIONS ||--o{ DECISION_LOGS : "session_id"
    SESSIONS ||--o| FEEDBACK : "session_id (unique)"
    KNOWLEDGE_CHUNKS ||--o{ EMBEDDING_JOBS : "chunk_id"

    FAQS ||..o{ KNOWLEDGE_CHUNKS : "source_type=faq"
    HISTORICAL_CASES ||..o{ KNOWLEDGE_CHUNKS : "source_type=historical_case"
    DIAGNOSTIC_TREES ||..o{ KNOWLEDGE_CHUNKS : "source_type=tree_node"

    VEHICLES {
        varchar vin PK
        varchar model
        varchar family
        int displacement_cc
        varchar market
        int model_year
        timestamp created_at
    }

    FAQS {
        bigint faq_id PK
        varchar model
        varchar category
        text question
        text answer
        int usage_count
        bool active
        timestamp created_at
        timestamp updated_at
    }

    DIAGNOSTIC_TREES {
        varchar tree_id PK
        varchar model
        varchar symptom
        int version
        jsonb tree_json
        bool active
        timestamp created_at
        timestamp updated_at
    }

    HISTORICAL_CASES {
        varchar case_id PK
        varchar model
        varchar symptom_category
        text case_text
        varchar final_diagnosis
        numeric base_confidence
        timestamp created_at
    }

    SESSIONS {
        uuid session_id PK
        varchar vin FK
        varchar model
        varchar entry_point
        varchar status
        timestamp started_at
        timestamp ended_at
        int total_steps
        varchar final_result
        bool success
    }

    SESSION_STATE {
        uuid session_id PK_FK
        varchar vin FK
        varchar model
        varchar current_symptom
        varchar current_node
        jsonb state_json
        timestamp updated_at
    }

    MESSAGES {
        bigint message_id PK
        uuid session_id FK
        varchar role
        text content
        timestamp created_at
    }

    DECISION_LOGS {
        bigint log_id PK
        uuid session_id FK
        varchar module_name
        jsonb input_data
        jsonb output_data
        timestamp created_at
    }

    FEEDBACK {
        bigint feedback_id PK
        uuid session_id FK_UK
        bool useful
        text comment
        timestamp created_at
    }

    KNOWLEDGE_CHUNKS {
        bigint chunk_id PK
        varchar source_type
        varchar source_id
        varchar model
        varchar symptom_category
        text text_chunk
        vector embedding
        tsvector lexical
        numeric base_confidence
        int chunk_index
        varchar embedding_provider
        varchar embedding_model
        jsonb metadata
        varchar embedding_status
        timestamp created_at
        timestamp updated_at
    }

    EMBEDDING_JOBS {
        bigint job_id PK
        bigint chunk_id FK
        varchar provider
        varchar model
        varchar status
        int attempts
        text last_error
        timestamp created_at
        timestamp updated_at
    }
```

> **Nota de diseño:** Los nodos del árbol de diagnóstico **no** tienen tabla propia. Se almacenan dentro del campo `tree_json JSONB` de `diagnostic_trees`, lo que permite versionar y actualizar árboles sin migraciones de esquema.

---

## API Endpoints

### Conversación (DDT)

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/session/start` | Crea sesión nueva, devuelve saludo o petición de VIN |
| `POST` | `/session/message` | Procesa mensaje, ejecuta grafo LangGraph |
| `GET` | `/session/{id}` | Detalle completo: metadatos + mensajes + diagnóstico |
| `POST` | `/session/{id}/feedback` | Registra 👍/👎 + comentario opcional |
| `GET` | `/health` | Estado del backend |

### Analítica y métricas

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/metrics/summary` | KPIs: sesiones, éxito, módulos, top diagnósticos, feedback |
| `GET` | `/analytics/sessions` | Lista paginada de sesiones (`limit`, `offset`, `status`) |
| `GET` | `/analytics/diagnoses` | Ranking de diagnósticos más frecuentes por modelo |
| `GET` | `/analytics/feedback` | Lista de feedback con resumen positivo/negativo |
| `GET` | `/analytics/heatmap` | Matriz síntomas × modelos para el mapa de calor |

### Base de conocimiento

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/knowledge/faqs` | Lista de FAQs (filtros: `model`, `category`) |
| `GET` | `/knowledge/cases` | Casos históricos (filtro: `model`) |
| `GET` | `/knowledge/trees` | Árboles DDT disponibles con recuento de nodos |

---

## Datos de prueba disponibles

### VINs de prueba (cargados por defecto)

| Modelo | VINs disponibles | Árboles DDT disponibles |
|---|---|---|
| AK550 | `AK550-POC-0001`, `AK550-POC-0002`, `AK550-POC-0003` | ✅ Motor, Arranque, CELP, Consumo |
| AK550 | `AK550-2020-0001`, `AK550-2021-0001`, `AK550-2023-0001` | ✅ Motor, Arranque, CELP, Consumo |
| AK550 Elite | `AK550E-2023-0001`, `AK550E-2024-0001`, `AK550E-POC-0001` | ❌ (Ruta B+C — sin árbol propio) |
| Xciting S 400 | `XCITING-POC-0001`, `XCITING-2022-0001`, `XCITING-2023-0001` | ✅ Motor |
| CV5 | `CV5-2023-0001`, `CV5-POC-0001`, `CV5-POC-0002` | ❌ (Ruta B+C) |
| DT X360 | `DTXS-2023-0001`, `DTXS-2024-0001`, `DTXS-POC-0001` | ❌ (Ruta B+C) |
| Agility 125 | `AGILITY-2022-0001`, `AGILITY-POC-0001`, `AGILITY-POC-0002` | ❌ (Ruta B+C) |

> **VIN recomendado para demos**: `AK550-POC-0001` (tiene todos los árboles DDT)

### Conocimiento cargado

| Tipo | Cantidad |
|---|---|
| FAQs curadas | 40 |
| Casos históricos | 76 (`CASE-001` a `CASE-076`) |
| Árboles DDT activos | 5 |
| Nodos de árbol | ~70 (almacenados en `tree_json JSONB`) |

---

## Estructura del proyecto

```
poc-asistente-tecnico/
│
├── docker-compose.yml              ← Orquesta los 3 contenedores
├── .env                            ← GROQ_API_KEY y config (no en Git)
├── ESTUDIAR.md                     ← Guía de estudio: DDT, tecnologías, flujos
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py                     ← Entry point FastAPI
│       ├── core/config.py          ← pydantic-settings: variables de entorno
│       ├── core/database.py        ← AsyncEngine + AsyncSession
│       ├── models/                 ← SQLAlchemy ORM: vehicle, session, knowledge, etc.
│       ├── api/
│       │   ├── routes/             ← session.py, metrics.py, analytics.py, knowledge.py
│       │   └── schemas/            ← Pydantic: contratos request/response
│       ├── orchestrator/
│       │   ├── graph.py            ← StateGraph LangGraph + funciones de enrutamiento
│       │   ├── state.py            ← ConversationState (TypedDict)
│       │   └── nodes/              ← vin_lookup, menu, classifier, faq_matcher, tree_engine, free_text
│       ├── services/
│       │   ├── groq_client.py      ← Wrapper Groq: LLM + embeddings
│       │   ├── ranking.py          ← Ranking híbrido (Ruta C)
│       │   ├── response_builder.py ← Contrato estándar de salida
│       │   └── tracing.py          ← Escribe decision_logs
│       └── db/
│           └── migrations/init.sql ← DDL + índices (auto-cargado al inicio)
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── App.jsx                 ← Layout: header + sidebar + chat
│       ├── services/api.js         ← Todas las llamadas fetch al backend
│       └── components/
│           ├── Chat/               ← ChatContainer, MessageBubble, MenuOptions, InputBar
│           ├── UI/                 ← SessionSummaryPanel, HealthIndicator, PhaseBar
│           └── Analytics/          ← LeftNavSidebar, SymptomHeatMap, PdfExport
│
└── docs/
    ├── DDT.md                      ← Documento de Diseño Técnico original
    ├── TECHNICAL_SPEC.md           ← Especificación técnica de todos los archivos
    └── FUNCTIONAL_OVERVIEW.md      ← Visión funcional para no técnicos
```

---

## Comandos útiles

```bash
# Arrancar todo (primera vez o tras cambios)
docker compose up --build

# Arrancar en segundo plano
docker compose up -d --build

# Ver logs en tiempo real
docker compose logs -f backend
docker compose logs -f frontend

# Reconstruir solo un servicio tras cambiar código
docker compose up -d --build backend
docker compose up -d --build frontend

# Reiniciar un contenedor sin rebuild
docker compose restart backend

# Parar todo
docker compose down

# Parar y borrar datos de BD (reset completo)
docker compose down -v

# Shell interactiva en el backend
docker exec -it poc-backend bash

# Consultar la BD directamente
docker exec -it poc-postgres psql -U poc_user -d poc_asistente

# Cargar seed SQL adicional
docker exec -i poc-postgres psql -U poc_user -d poc_asistente < database/migrations/seed.sql
```

---

## Desarrollo local (sin Docker)

```bash
# Terminal 1 — Backend
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev
# Abre http://localhost:5173 (Vite dev server)
```

> Para el backend local necesitas PostgreSQL accesible. La forma más simple es levantar solo la BD con Docker:
> ```bash
> docker compose up -d postgres
> ```

---

## Variables de entorno (`.env`)

| Variable | Ejemplo | Descripción |
|---|---|---|
| `GROQ_API_KEY` | `gsk_...` | Clave API de Groq (obligatoria) |
| `DATABASE_URL` | `postgresql+asyncpg://poc_user:poc_password@poc-postgres:5432/poc_asistente` | Conexión asyncpg |
| `GROQ_MODEL` | `llama-3.1-8b-instant` | Modelo LLM para clasificación y narrativa |
| `GROQ_EMBEDDING_MODEL` | `nomic-embed-text-v1_5` | Modelo para embeddings (768 dim) |
| `SIMILARITY_THRESHOLD` | `0.75` | Umbral mínimo de similitud para Ruta B (FAQ) |
| `TOP_K_RESULTS` | `3` | Número de hipótesis en Ruta C |
| `FRONTEND_ORIGIN` | `http://localhost:3000` | CORS origin permitido |

---

## Panel de Analítica

El sidebar del chat ofrece 7 secciones:

| Sección | Icono | Qué muestra |
|---|---|---|
| Métricas | 📊 | KPIs: sesiones, tasa de éxito, módulos más usados, top diagnósticos |
| Sesiones | 🗂️ | Lista paginada de sesiones con estado y duración |
| Diagnósticos | 🔎 | Ranking de diagnósticos frecuentes por modelo |
| Feedback | 💬 | Valoraciones 👍/👎 con comentarios |
| Conocimiento | 📚 | FAQs, casos históricos y árboles DDT consultables |
| Mapa de calor | 🌡️ | Matriz síntomas × modelos: intensidad de actividad |
| Exportar PDF | 📄 | Genera informe PDF en el navegador (sin librerías externas) |

---

## Reglas de negocio clave

| Código | Regla |
|---|---|
| RN-NEG-001 | Sin VIN válido no hay diagnóstico. El sistema nunca asume el vehículo |
| RN-NEG-002 | El modelo lo determina el VIN, nunca el texto del usuario |
| RN-NEG-003 | Síntoma conocido + árbol disponible → prioridad a Ruta A (DDT) |
| RN-NEG-006 | En Ruta C, los casos históricos se filtran por modelo del vehículo |
| RN-NEG-007 | Si el árbol llega a un nodo fuera del alcance del POC, se emite respuesta controlada |
| RN-NEG-009 | Máximo 3 intentos de VIN antes de cerrar sesión en error |

---

## Checklist de verificación

```
[ ] docker compose up --build       →  sin errores de build
[ ] GET  http://localhost:8000/health              →  {"status":"ok"}
[ ] POST http://localhost:8000/session/start       →  devuelve session_id
[ ] VIN "AK550-POC-0001"            →  menú de 6 opciones aparece
[ ] Seleccionar "Paradas de motor"  →  primera pregunta Sí/No del árbol DDT
[ ] Responder Sí/No varias veces   →  diagnóstico final con hipótesis
[ ] POST /session/{id}/feedback     →  {"ok":true}
[ ] GET  http://localhost:8000/metrics/summary     →  datos de métricas
[ ] GET  http://localhost:8000/analytics/heatmap   →  matriz modelos×síntomas
[ ] http://localhost:3000           →  chat funcional con sidebar de analítica
```
