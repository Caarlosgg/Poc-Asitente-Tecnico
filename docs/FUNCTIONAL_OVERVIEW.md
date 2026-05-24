# Visión Funcional del Proyecto — Asistente Técnico de Diagnóstico

> **Para**: Presentación al equipo directivo / no técnico  
> **Propósito**: Explicar qué hemos construido, cómo funciona, qué tecnologías usamos y por qué, sin entrar en código.  
> **Actualizado**: Mayo 2025

---

## ¿Qué es este sistema?

Hemos construido un **asistente conversacional inteligente** para técnicos de taller, capaz de:

1. **Identificar el vehículo** por número de bastidor (VIN).
2. **Guiar al técnico** a través de un diagnóstico paso a paso mediante preguntas Sí/No.
3. **Consultar una base de conocimiento** de preguntas frecuentes, casos históricos y protocolos técnicos.
4. **Dar un diagnóstico final** con la hipótesis principal, alternativas, nivel de confianza y próximo paso recomendado.
5. **Recoger feedback** del técnico sobre la utilidad del diagnóstico.
6. **Mostrar analíticas** en tiempo real: métricas de uso, mapa de calor de síntomas por modelo, historial de sesiones.

Es una **prueba de concepto (POC)** — funcional y desplegable, pero diseñada para demostrar las capacidades antes de una implementación en producción.

---

## ¿Cómo usa el técnico el sistema?

### Flujo de uso — paso a paso

```
┌─────────────────────────────────────────────────────────┐
│  1. El técnico abre la aplicación en el navegador       │
│     → URL: http://localhost:3000                        │
└───────────────────────────┬─────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│  2. El asistente saluda y pide el número de bastidor    │
│     "Hola, ¿cuál es el número de bastidor del vehículo?"│
└───────────────────────────┬─────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│  3. Técnico escribe el VIN (ej. AK550-2023-001)         │
│     → El sistema lo identifica: "AK550 2023, ¡listo!"  │
└───────────────────────────┬─────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│  4. Menú de síntomas (tarjetas visuales)                │
│     ⚡ Paradas de motor    🔑 Problemas de arranque      │
│     ⚠️ Testigo CELP        ⛽ Consumo excesivo           │
│     📚 Consulta FAQ        💬 Descripción libre          │
└───────────────────────────┬─────────────────────────────┘
                            ↓
           ┌────────────────┼────────────────┐
           ↓                ↓                ↓
      RUTA A          RUTA B           RUTA C
  Árbol DDT        Base FAQ         IA + Historial
  (preguntas       (respuesta       (texto libre,
   Sí/No)          inmediata)       LLM analiza)
           └────────────────┼────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│  5. Diagnóstico final                                   │
│     ✅ Hipótesis: "Válvula EGR obstruida"               │
│     📊 Confianza: 87%                                   │
│     🔧 Próximo paso: "Inspeccionar circuito EGR"        │
└───────────────────────────┬─────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│  6. Feedback                                            │
│     "¿Ha sido útil este diagnóstico?"  👍 / 👎          │
│     (Opcionalmente, comentario de texto)                │
└─────────────────────────────────────────────────────────┘
```

---

## Las tres rutas de diagnóstico

El sistema decide automáticamente qué ruta tomar según la elección del técnico:

### Ruta A — Árbol de Decisión Diagnóstica (DDT)
**Cuándo**: El técnico selecciona un síntoma específico (motor, arranque, CELP, consumo).

**Cómo funciona**: El sistema sigue un protocolo técnico predefinido por el fabricante — el **DDT (Decision Diagnostic Tree)**. Es una secuencia de preguntas binarias (Sí/No) que va descartando causas hasta llegar a un diagnóstico concreto.

**Ejemplo** (árbol de paradas de motor en AK550):
```
¿El motor se para en caliente?
  → Sí → ¿Hay humo negro por el escape?
              → Sí → Diagnóstico: Inyector defectuoso
              → No → ¿La ralentí es inestable?
                          → ...
  → No → ¿Se para al dar gas bruscamente?
              → ...
```

**Ventaja**: Diagnóstico reproducible, basado en protocolo oficial. El técnico puede confiar en el resultado.

---

### Ruta B — Base de Conocimiento (FAQ)
**Cuándo**: El técnico selecciona "Consulta FAQ" o tiene una pregunta de mantenimiento/procedimiento.

**Cómo funciona**: El sistema busca en una base de **40 preguntas frecuentes** curadas por el equipo técnico. Devuelve la respuesta más relevante de forma instantánea.

**Ejemplo**:
- Pregunta: "¿Cada cuántos km se cambia el aceite en el AK550?"
- Respuesta: "El intervalo recomendado es 3.000 km o 6 meses para el primer cambio, y cada 6.000 km o 12 meses posteriormente."

---

### Ruta C — Análisis Libre por Inteligencia Artificial
**Cuándo**: El técnico describe el problema con sus propias palabras (no encaja en los síntomas del menú).

**Cómo funciona**: 
1. El sistema busca en **76 casos históricos** de averías anteriores similares.
2. Complementa con el LLM (modelo de lenguaje) para analizar la descripción y sintetizar un diagnóstico.
3. Si detecta que el problema encaja con un árbol DDT disponible, sugiere cambiar a Ruta A.

**Ejemplo**:
- Técnico escribe: "El cliente dice que la moto tiembla mucho al frenar en cuesta abajo"
- Sistema busca casos similares + analiza → Diagnóstico: "Posible disco de freno alabeado, confianza 72%"

---

## El DDT — ¿qué es y por qué es importante?

El **DDT (Decision Diagnostic Tree)** es el corazón técnico del sistema.

Un DDT es un protocolo diagnóstico estructurado:
- Definido por el fabricante o el equipo de ingeniería
- Formado por una secuencia de preguntas binarias (Sí/No)
- Cada respuesta lleva a un nodo diferente
- Los nodos finales son diagnósticos concretos con acción recomendada

**Árboles disponibles en el sistema**:

| Árbol | Modelo | Síntoma | Nodos |
|-------|--------|---------|-------|
| AK550_MOTOR_V1 | AK550 2023 | Paradas de motor | ~15 |
| AK550_ARRANQUE_V1 | AK550 2023 | Problemas de arranque | ~12 |
| AK550_CELP_V1 | AK550 2023 | Testigo CELP | ~10 |
| AK550_CONSUMO_V1 | AK550 2023 | Consumo excesivo | ~15 |
| XCITING400_MOTOR_V1 | Xciting 400 | Paradas de motor | ~10 |

**¿Por qué es importante?**
- Garantiza que todos los técnicos siguen el mismo protocolo
- El diagnóstico es auditable (queda registrado en la base de datos)
- Reduce el tiempo de diagnóstico (promedio actual: ~7 preguntas por sesión)
- Elimina diagnósticos subjetivos basados en la experiencia individual

---

## ¿Cómo está relacionada la base de datos?

La base de datos guarda todo lo que ocurre en el sistema. Las entidades principales son:

### Relación entre tablas

```
VEHÍCULO (vehicles)
  │  VIN, modelo, año, color, km
  │
  └── SESIÓN (sessions)
        │  ¿Qué vehículo?, ¿por qué síntoma entró?,
        │  ¿cuándo empezó/terminó?, ¿cuál fue el diagnóstico?
        │
        ├── MENSAJES (messages)
        │     Todo el chat: quién dijo qué y cuándo
        │
        ├── ESTADO DE SESIÓN (session_state)
        │     Dónde está el técnico dentro del árbol DDT en este momento
        │     (si cierra y vuelve, puede continuar)
        │
        ├── LOGS DE DECISIÓN (decision_logs)
        │     Trazabilidad: qué módulo tomó cada decisión y por qué
        │
        └── FEEDBACK (feedback)
              ¿Fue útil el diagnóstico? + comentario opcional

ÁRBOL DDT (diagnostic_trees)
  └── NODOS (tree_nodes)
        Cada pregunta/diagnóstico del árbol y sus conexiones

FAQS (faqs)
  Preguntas frecuentes curadas

CASOS HISTÓRICOS (historical_cases)
  Averías anteriores documentadas con su solución
```

### Campos clave que conviene conocer

| Campo | Tabla | Significado |
|-------|-------|-------------|
| `vin` | sessions | Número de bastidor — identifica el vehículo |
| `entry_point` | sessions | Por qué síntoma entró el técnico (symptom_motor, faq, other…) |
| `final_result` | sessions | Diagnóstico final dado por el sistema |
| `total_steps` | sessions | Cuántas preguntas se hicieron en total |
| `current_node` | session_state | En qué pregunta del árbol estamos ahora mismo |
| `confidence` | (DiagnosisData) | Confianza del diagnóstico (0-100%) |
| `source_type` | (DiagnosisData) | De dónde viene el diagnóstico: árbol/faq/historial |

---

## Tecnologías utilizadas y por qué

### Backend (servidor)
| Tecnología | Versión | Por qué la usamos |
|------------|---------|-------------------|
| **Python** | 3.12 | Lenguaje más extendido para IA/ML. Ecosistema maduro. |
| **FastAPI** | 0.115.2 | Framework web moderno, muy rápido, genera documentación automática en `/docs`. |
| **PostgreSQL** | 16 | Base de datos relacional robusta, de código abierto, con extensión pgvector para búsqueda semántica futura. |
| **SQLAlchemy** | 2.0 | ORM (mapeador objeto-relacional) que permite trabajar con la BD en Python sin escribir SQL directamente. Versión async para mejor rendimiento. |
| **LangGraph** | 0.2.28 | Librería de Langchain para definir flujos conversacionales como grafos de estados. Permite pausar y reanudar conversaciones entre mensajes. |
| **Groq API** | 0.11.0 | Servicio de LLM (modelo de lenguaje grande) ultra-rápido. Usamos `llama-3.1-8b-instant` para la Ruta C (análisis libre). Gratuito en el tier de uso actual. |

### Frontend (interfaz visual)
| Tecnología | Versión | Por qué la usamos |
|------------|---------|-------------------|
| **React** | 18.3.1 | Librería de UI más popular del mercado. Componentes reutilizables, gestión de estado reactiva. |
| **Vite** | 5.4.2 | Bundler moderno, compilación en < 4 segundos. Mucho más rápido que Webpack. |
| **Tailwind CSS** | 3.x | Framework de estilos utility-first. Permite diseñar directamente en HTML sin escribir CSS separado. Tema oscuro consistente. |

### Infraestructura
| Tecnología | Por qué la usamos |
|------------|-------------------|
| **Docker** | Empaqueta cada servicio en un contenedor aislado. "Funciona en cualquier máquina". |
| **Docker Compose** | Orquesta los 3 contenedores (BD, backend, frontend) con un solo comando. |

---

## Arquitectura — cómo fluye la información

```
┌────────────────────────────────────────────────────────┐
│               NAVEGADOR DEL TÉCNICO                    │
│                                                        │
│  ┌──────────────┐    ┌───────────────────────────────┐ │
│  │   Sidebar    │    │         Chat                  │ │
│  │  Analítica   │    │  ┌─────────────────────────┐  │ │
│  │              │    │  │   Mensajes del técnico  │  │ │
│  │  📊 Métricas │    │  │   Respuestas asistente  │  │ │
│  │  🗂️ Sesiones │    │  │   Menú de síntomas      │  │ │
│  │  🌡️ Mapa     │    │  │   Diagnóstico final     │  │ │
│  │  📄 PDF      │    │  └─────────────────────────┘  │ │
│  └──────────────┘    └───────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
                   │ HTTP REST
                   ↓
┌────────────────────────────────────────────────────────┐
│              SERVIDOR BACKEND (FastAPI)                 │
│                                                        │
│  Recibe mensaje → Determina contexto → Ejecuta grafo  │
│                                                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │              GRAFO LANGGRAPH                    │   │
│  │                                                 │   │
│  │  [dispatch] → [vin_lookup] → [show_menu]        │   │
│  │                    ↓                            │   │
│  │  [classifier] → [tree_engine] ← síntoma         │   │
│  │              → [faq_matcher]  ← consulta        │   │
│  │              → [free_text]    ← descripción     │   │
│  │                    ↓                            │   │
│  │            [response_builder]                   │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
                   │ SQL async
                   ↓
┌────────────────────────────────────────────────────────┐
│              BASE DE DATOS (PostgreSQL)                 │
│                                                        │
│   vehicles · sessions · messages · session_state       │
│   diagnostic_trees · tree_nodes · faqs                 │
│   historical_cases · decision_logs · feedback          │
└────────────────────────────────────────────────────────┘
                   │ API REST
                   ↓
            ┌──────────────┐
            │  GROQ API    │
            │ LLM externo  │
            │ (Ruta C)     │
            └──────────────┘
```

---

## Panel de analítica — ¿qué podemos ver?

El sidebar izquierdo ofrece 7 secciones de analítica en tiempo real:

| Sección | Qué muestra |
|---------|------------|
| **📊 Métricas** | Total de sesiones, tasa de éxito, pasos promedio, uso por módulo (árbol/FAQ/libre), feedback positivo/negativo |
| **🗂️ Sesiones** | Las últimas sesiones: vehículo, estado (activa/completada), diagnóstico, duración |
| **🔎 Diagnósticos** | Ranking de los diagnósticos más frecuentes con barras de progreso relativo |
| **💬 Feedback** | Resumen valoraciones + comentarios de los técnicos |
| **📚 Conocimiento** | Árboles DDT disponibles / FAQs cargadas / Casos históricos |
| **🌡️ Mapa de calor** | Grid visual: eje X = modelos, eje Y = síntomas, colores = frecuencia. De un vistazo ves qué falla más en cada modelo. |
| **📄 Exportar PDF** | Genera un informe descriptivo completo (KPIs + sesiones + diagnósticos + feedback) listo para imprimir o guardar como PDF |

### Mapa de calor — ejemplo visual

```
               AK550 2023   Xciting 400   XTOWN 300
Paradas motor  ██████████   ███           
Arranque       █████        █████████     ██
CELP           ███          ██            ████████████
Consumo        ██████████   ████          █

■ Rojo=crítico  ■ Naranja=alto  ■ Amarillo=medio  ■ Verde=bajo
```

---

## Datos de demostración disponibles

El sistema viene con datos precargados para poder demostrar todas las funcionalidades:

| Tipo | Cantidad | Modelos |
|------|----------|---------|
| Vehículos (VINs) | 44 | AK550, Xciting 400, X-Town 300, AK125, AK550 Euro5, Xciting S400 |
| Árboles DDT | 5 | AK550 (4 síntomas) + Xciting400 (1 síntoma) |
| FAQs curadas | 40 | Mantenimiento, consumos, CELP, procedimientos |
| Casos históricos | 76 | CASE-001 a CASE-076 |

### VINs de ejemplo para demostrar

```
AK550 2023:      AK550-2023-001 al AK550-2023-009
Xciting 400:     XCT400-2022-001 al XCT400-2022-005
X-Town 300:      XT300-2021-001 al XT300-2021-003
```

---

## Flujo del asistente — diagrama completo

```
INICIO DE SESIÓN
      │
      ▼
¿Tiene VIN?
  NO → Pedir VIN → Usuario escribe VIN → Verificar en BD
  SÍ → (recuperar sesión)
      │
      ▼
VIN válido → Identificar modelo
      │
      ▼
MENÚ PRINCIPAL
(6 opciones visuales)
      │
    ┌─┼──────────────────────────────┐
    ▼ ▼                              ▼
RUTA A              RUTA B         RUTA C
Síntoma             FAQ            Descripción libre
    │               │              │
    ▼               ▼              ▼
Árbol DDT       Búsqueda        Búsqueda en
(nodo raíz)     en FAQs         historial + LLM
    │               │              │
    ▼               ▼              │
Preguntas      Respuesta        ¿Encaja con
Sí/No          inmediata        árbol DDT?
    │                            Sí→ sugerir Ruta A
    ▼                            No→ diagnóstico libre
Nodo final
    │
    └──────────────────────────────┐
                                   ▼
                          DIAGNÓSTICO FINAL
                    (hipótesis + confianza + siguiente paso)
                                   │
                                   ▼
                            FEEDBACK (👍/👎)
                                   │
                                   ▼
                          ¿Nueva consulta? → MENÚ
```

---

## Puntos fuertes del sistema

1. **Diagnóstico reproducible**: Dos técnicos con el mismo vehículo y síntoma recibirán el mismo diagnóstico DDT.
2. **Trazabilidad completa**: Cada decisión queda registrada — quién consultó, qué respondió, cuál fue el resultado.
3. **Aprendizaje continuo**: Los casos históricos se acumulan y la Ruta C mejora con más datos.
4. **Analítica integrada**: El supervisor puede ver en tiempo real qué modelos dan más problemas y qué síntomas son más frecuentes.
5. **Sin instalación en cliente**: Se accede desde el navegador web — sin instalar nada en los PCs del taller.
6. **Exportable**: Informe PDF descargable en cualquier momento para reuniones o auditorías.

---

## Limitaciones actuales del POC

| Limitación | Impacto | Solución futura |
|------------|---------|-----------------|
| Árboles solo para AK550 y Xciting400 | Los demás modelos solo tienen Ruta C | Añadir árboles para el resto de modelos |
| Sin autenticación | Cualquiera con acceso puede usar el sistema | Añadir login de técnico |
| LLM externo (Groq) | Dependencia de internet para Ruta C | Modelo local en producción |
| Sin embeddings vectoriales | Búsqueda FAQ y historial solo lexical | Activar pgvector con embeddings reales |
| Un solo idioma (español) | Solo técnicos hispanos | Añadir i18n |

---

*Documento funcional — POC Asistente Técnico de Diagnóstico · Mayo 2025*
