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
   - `AK550-2023-001` (AK550 — tiene árboles DDT completos)
   - `XCT400-2022-001` (Xciting S 400)
   - `CV5-2023-001` (CV5 — solo FAQ + texto libre)
3. Elige un síntoma del menú y sigue el flujo guiado

> **VINs de prueba recomendados:**
> - `AK550-POC-0001` → AK550 con árboles DDT completos (Motor, Arranque, CELP, Consumo)
> - `XCITING-POC-0001` → Xciting S 400 con árbol de Motor
> - `CV5-2023-0001` → CV5, solo Ruta B (FAQ) + Ruta C (IA libre)

---

## Cómo funciona — Las tres rutas

```
USUARIO
  │
  ▼
Pedir bastidor (VIN)
  │
  ▼ [vin_lookup] — Verifica en BD vehicles
  │
  ▼ [show_menu] — Muestra 6 opciones
  │
  ├────────────────────────────────────────────────────────┐
  │                        │                              │
  ▼                        ▼                              ▼
RUTA A                  RUTA B                        RUTA C
Síntomas conocidos      FAQ                         Texto libre
[tree_engine]        [faq_matcher]             [free_text_node]
Navega árbol DDT     Búsqueda en BD de FAQs    Historial + LLM (Groq)
Preguntas Sí/No      Respuesta curada          Respuesta contextual
  │                        │                              │
  └────────────────────────┴──────────────────────────────┘
                           │
                   [response_builder]
                           │
             Diagnóstico estructurado
         (hipótesis + confianza + siguiente paso)
                           │
                  Feedback 👍 / 👎
```

| Ruta | Cuándo se activa | Tecnología |
|---|---|---|
| **A — Árbol DDT** | Síntoma conocido con árbol disponible para el modelo | `tree_engine` navega nodos Sí/No |
| **B — FAQ** | Pregunta frecuente / consulta no diagnóstica | `faq_matcher` búsqueda lexical en BD |
| **C — Texto libre** | Sin árbol disponible o pregunta abierta | Historial de casos + Groq LLM |

---

## Arquitectura del sistema

```
┌─────────────────────────────────────────────────────────┐
│                    NAVEGADOR                            │
│                                                         │
│  ┌─────────────────┐    ┌──────────────────────────────┐│
│  │  Sidebar        │    │       Chat                   ││
│  │  Analítica      │    │  ┌──────────────────────────┐││
│  │  ─────────────  │    │  │ MessageBubble            │││
│  │  📊 Métricas    │    │  │ MenuOptions (tarjetas)   │││
│  │  🗂️ Sesiones    │    │  │ DiagnosisResult          │││
│  │  🔎 Diagnóst.   │    │  │ InputBar                 │││
│  │  💬 Feedback    │    │  └──────────────────────────┘││
│  │  📚 Conocim.    │    └──────────────────────────────┘│
│  │  🌡️ Mapa calor  │                                    │
│  │  📄 Export PDF  │         React 18 · Tailwind CSS    │
│  └─────────────────┘         Vite 5 · Puerto 3000       │
└───────────────────────────────┬─────────────────────────┘
                                │ REST / JSON
                                ▼
┌─────────────────────────────────────────────────────────┐
│           FastAPI · Python 3.12 · Puerto 8000           │
│                                                         │
│   /session/start     →  [dispatch] → [vin_lookup]       │
│   /session/message   →  [LangGraph StateGraph]          │
│   /session/{id}      →  BD: session + messages          │
│   /metrics/summary   →  KPIs agregados                  │
│   /analytics/*       →  Sesiones, diagnósticos, heatmap │
│   /knowledge/*       →  FAQs, casos, árboles            │
│                                                         │
│        LangGraph 0.2.28 · Pydantic 2 · SQLAlchemy 2     │
└───────────────────────────┬─────────────────────────────┘
                            │ asyncpg
                            ▼
┌─────────────────────────────────────────────────────────┐
│         PostgreSQL 16 + pgvector · Puerto 5432          │
│                                                         │
│  vehicles  sessions  messages  session_state            │
│  decision_logs  feedback  diagnostic_trees  tree_nodes  │
│  faqs  historical_cases                                 │
└─────────────────────────────────────────────────────────┘
                            │ API REST
                            ▼
                   ┌─────────────────┐
                   │   Groq API      │
                   │ llama-3.1-8b    │
                   │  (solo Ruta C)  │
                   └─────────────────┘
```

### LangGraph — el grafo de conversación

```
[dispatch]
    │
    ├── sin VIN → [request_vin] ──────► [vin_lookup]
    │                                        │
    │                               ┌────────┴─────────┐
    │                          VIN válido         No válido
    │                               │            (máx 3 intentos)
    │                               ▼                  │
    │                          [show_menu]    [session_end_error]
    │                               │
    │              ┌────────────────┼────────────────┐
    │              ▼                ▼                ▼
    │        síntoma A           FAQ B          libre C
    │       [classifier]     [faq_matcher]  [free_text_node]
    │            │
    │      [await_input] ←────────────────────┐
    │            │                            │
    │       [tree_engine] → pregunta Sí/No ───┘
    │            │
    │     (cuando hay diagnóstico)
    │            ▼
    │    [response_builder]
    │            │
    └─────────► END
```

---

## Base de datos — relaciones

```mermaid
erDiagram
    VEHICLES ||--o{ SESSIONS : "vin"
    SESSIONS ||--|| SESSION_STATE : "session_id"
    SESSIONS ||--o{ MESSAGES : "session_id"
    SESSIONS ||--o{ DECISION_LOGS : "session_id"
    SESSIONS ||--o| FEEDBACK : "session_id"
    DIAGNOSTIC_TREES ||--o{ TREE_NODES : "tree_id"

    VEHICLES {
        varchar vin PK
        varchar model
        int year
        varchar color
        int km
    }

    SESSIONS {
        uuid session_id PK
        varchar vin FK
        varchar model
        varchar entry_point
        varchar status
        int total_steps
        varchar final_result
        bool success
        timestamp started_at
        timestamp ended_at
    }

    SESSION_STATE {
        uuid session_id PK_FK
        varchar current_node
        varchar current_symptom
        jsonb state_json
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
        text input_summary
        text output_summary
    }

    FEEDBACK {
        int feedback_id PK
        uuid session_id FK
        bool useful
        text comment
    }

    DIAGNOSTIC_TREES {
        varchar tree_id PK
        varchar model
        varchar symptom
        bool is_active
    }

    TREE_NODES {
        varchar node_id PK
        varchar tree_id FK
        varchar node_type
        text content
        varchar yes_next
        varchar no_next
    }

    FAQS {
        int faq_id PK
        varchar model
        varchar category
        text question
        text answer
    }

    HISTORICAL_CASES {
        varchar case_id PK
        varchar model
        varchar symptom_category
        text description
        text resolution
        float confidence_score
    }
```

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
| Nodos de árbol | ~70 |

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
│   └── app/
│       ├── main.py                 ← Entry point FastAPI
│       ├── core/config.py          ← pydantic-settings: variables de entorno
│       ├── db/
│       │   ├── session.py          ← AsyncEngine + AsyncSession
│       │   └── schema.py           ← Tablas SQLAlchemy ORM
│       ├── api/
│       │   ├── routers/            ← session.py, metrics.py, analytics.py, knowledge.py
│       │   └── schemas/            ← Pydantic: contratos request/response
│       └── modules/
│           ├── orchestrator/       ← StateGraph LangGraph + ConversationState
│           ├── vin_lookup/         ← Valida bastidor contra tabla vehicles
│           ├── tree_engine/        ← Navega árbol DDT nodo a nodo
│           ├── faq_matcher/        ← Búsqueda lexical en FAQs
│           ├── free_text_parser/   ← Texto libre → contexto para LLM
│           ├── response_builder/   ← Formatea DiagnosisData estructurado
│           └── traceability/       ← Escribe decision_logs
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
├── database/
│   └── migrations/                 ← init.sql: DDL + seeds auto-cargados
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
uvicorn app.main:app --host 0.0.0.0 --port 8000

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
| `GROQ_MODEL` | `llama-3.1-8b-instant` | Modelo LLM |
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
