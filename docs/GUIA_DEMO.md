# Guía de Demostración — Asistente Técnico de Diagnóstico Kymco

> **Audiencia:** Técnicos, evaluadores y cualquier persona que acceda al sistema por primera vez.  
> **URL local:** `http://localhost:3000` (frontend) · `http://localhost:8000` (API)

---

## 1. Qué es este sistema

El **Asistente Técnico de Diagnóstico Kymco** es un chatbot guiado que ayuda al técnico a diagnosticar averías de motocicletas mediante tres rutas complementarias:

| Ruta | Cuándo se activa | Qué hace |
|------|-----------------|----------|
| 🌳 **A — Árbol guiado** | Síntoma seleccionado del menú | Pregunta paso a paso hasta llegar a un diagnóstico determinístico |
| 📋 **B — FAQ** | Usuario elige "Consultas frecuentes" | Busca en la base de conocimiento la pregunta más parecida |
| 🔍 **C — Historial** | Descripción libre del problema | Recupera casos históricos similares y genera una hipótesis |

---

## 2. Vehículos disponibles en la base de datos

### 🏍️ AK550 — Sport Maxi 550cc

| Bastidor (VIN) | Año | Mercado | Notas |
|----------------|-----|---------|-------|
| `AK550-POC-0001` | 2023 | ES | Bastidor de prueba principal |
| `AK550-POC-0002` | 2023 | ES | Bastidor de prueba |
| `AK550-POC-0003` | 2023 | ES | Bastidor de prueba |
| `AK550-POC-0004` | 2023 | ES | Bastidor adicional |
| `AK550-POC-0005` | 2024 | ES | Bastidor adicional |
| `AK550-2020-0001` | 2020 | ES | Serie real |
| `AK550-2020-0002` | 2020 | ES | Serie real |
| `AK550-2021-0001` | 2021 | ES | Serie real |
| `AK550-2022-0001` | 2022 | ES | Serie real |
| `AK550-2022-0002` | 2022 | ES | Serie real |
| `AK550-2023-0001` | 2023 | ES | Serie real |
| `AK550-2023-0002` | 2023 | FR | Serie real mercado francés |
| `AK550-2024-0001` | 2024 | ES | Serie real |
| `AK550-2025-0001` | 2025 | ES | Serie reciente |

**Árboles de diagnóstico disponibles para AK550:**
- `AK550_MOTOR_V1` — Paradas de motor (9 nodos)
- `AK550_ARRANQUE_V1` — Problemas de arranque (13 nodos)
- `AK550_CELP_V1` — Testigo CELP encendido (5 nodos)
- `AK550_CONSUMO_V1` — Consumo excesivo (15 nodos) ← *nuevo*

---

### 🏍️ AK550 Elite — Sport Maxi Premium 550cc

| Bastidor (VIN) | Año | Mercado |
|----------------|-----|---------|
| `AK550E-2023-0001` | 2023 | ES |
| `AK550E-2024-0001` | 2024 | ES |
| `AK550E-POC-0001`  | 2023 | ES |
| `AK550E-POC-0002`  | 2024 | ES |
| `AK550E-2025-0001` | 2025 | ES |

> El AK550 Elite comparte árboles con el AK550. Al identificarlo, el menú mostrará las mismas opciones de síntoma.

---

### 🏍️ Xciting S 400 — Sport Maxi 400cc

| Bastidor (VIN) | Año | Mercado |
|----------------|-----|---------|
| `XCITING-POC-0001` | 2022 | ES |
| `XCITING-POC-0002` | 2023 | ES |
| `XCITING-POC-0003` | 2024 | ES |
| `XCITING-2022-0001` | 2022 | ES |
| `XCITING-2023-0001` | 2023 | ES |
| `XCITING-2024-0001` | 2024 | ES |
| `XCITING-2024-0002` | 2024 | DE |
| `XCITING-2025-0001` | 2025 | ES |

**Árbol disponible para Xciting S 400:**
- `XCITING_MOTOR_V1` — Paradas de motor (11 nodos)

---

### ⚡ CV5 — Scooter eléctrico

| Bastidor (VIN) | Año | Mercado |
|----------------|-----|---------|
| `CV5-2023-0001`  | 2023 | ES |
| `CV5-POC-0001`   | 2023 | ES |
| `CV5-POC-0002`   | 2024 | ES |
| `CV5-POC-0003`   | 2024 | ES |
| `CV5-2024-0001`  | 2024 | ES |
| `CV5-2024-0002`  | 2024 | FR |
| `CV5-2025-0001`  | 2025 | ES |

> El CV5 es eléctrico (sin cilindrada). El asistente adapta el menú automáticamente. Ideal para probar la ruta de descripción libre (Ruta C) con síntomas eléctricos.

---

### 🏁 DT X360 — Adventure 350cc

| Bastidor (VIN) | Año | Mercado |
|----------------|-----|---------|
| `DTXS-2023-0001` | 2023 | ES |
| `DTXS-2024-0001` | 2024 | ES |
| `DTXS-POC-0001`  | 2023 | ES |
| `DTXS-POC-0002`  | 2024 | ES |
| `DTXS-2025-0001` | 2025 | ES |

---

### 🛵 Agility 125 — Scooter urbano 125cc

| Bastidor (VIN) | Año | Mercado |
|----------------|-----|---------|
| `AGILITY-2022-0001` | 2022 | ES |
| `AGILITY-POC-0001`  | 2022 | ES |
| `AGILITY-POC-0002`  | 2023 | ES |
| `AGILITY-2023-0001` | 2023 | ES |
| `AGILITY-2024-0001` | 2024 | ES |

---

## 3. Cómo usar el sistema — Paso a paso

### 3.1 Inicio de sesión

1. Abrir el navegador en `http://localhost:3000`
2. El asistente saluda y pide el **bastidor (VIN)**
3. Escribir cualquiera de los bastidores de la tabla anterior (p.ej. `AK550-POC-0001`)
4. El sistema identifica el vehículo y muestra el **menú de síntomas**

> ⚠️ El bastidor debe estar en la tabla `vehicles`. Si se escribe uno desconocido, el asistente pedirá que lo corrijas (hasta 3 intentos).

---

### 3.2 Ruta A — Diagnóstico guiado por árbol 🌳

**Cuándo usarla:** Cuando el técnico sabe qué categoría de síntoma tiene el vehículo.

**Pasos:**
1. Identificar vehículo (p.ej. `AK550-POC-0001`)
2. Elegir un síntoma del menú: *🔧 Paradas de motor*, *🔩 Problemas de arranque*, etc.
3. Responder las preguntas con **Sí / No** (o las opciones mostradas)
4. El sistema avanza por el árbol hasta emitir un **diagnóstico final**
5. Ver el resultado: causa probable, nivel de confianza (90%), siguiente comprobación

**Ejemplo completo — AK550 Arranque:**
```
Bastidor:   AK550-POC-0001
Síntoma:    🔩 Problemas de arranque
Q1: ¿Al pulsar arranque, gira el motor? → No
Q2: ¿Batería cargada? → Sí
Q3: ¿Fusibles OK? → Sí
→ Diagnóstico: Relé de arranque defectuoso
```

**Ejemplo completo — AK550 Consumo excesivo (árbol nuevo):**
```
Bastidor:   AK550-POC-0004
Síntoma:    ⛽ Consumo excesivo
Q1: ¿Aumentó de forma repentina tras un cambio? → No
Q2: ¿Uso principalmente en ciudad? → Sí
Q3: ¿Ralentí estable? → No
→ Diagnóstico: Ralentí desajustado o depósito de carbón en válvula IAC
```

---

### 3.3 Ruta B — Consultas frecuentes (FAQ) 📋

**Cuándo usarla:** El técnico tiene una duda técnica concreta, no una avería.

**Pasos:**
1. Identificar vehículo
2. Elegir *📋 Consultas frecuentes*
3. Seleccionar la categoría temática (o escribir la pregunta directamente)
4. El sistema busca y devuelve la FAQ más relevante con la respuesta

**Preguntas frecuentes de ejemplo:**
- `Mantenimiento` — ¿Cada cuánto km hacer el reglaje de válvulas?
- `Batería` — ¿Qué batería usa el AK550?
- `Consumo` — ¿Cuál es el consumo normal del AK550?
- `Arranque` — El motor gira pero no enciende en frío
- `Testigo CELP` — ¿Puedo seguir circulando con el CELP encendido?

---

### 3.4 Ruta C — Descripción libre del problema 🔍

**Cuándo usarla:** El técnico describe el síntoma con sus propias palabras.

**Pasos:**
1. Identificar vehículo
2. Elegir *💬 Describir el problema*
3. Escribir libremente la descripción del síntoma
4. El sistema analiza los tags, busca en el historial de 76 casos y emite una hipótesis

**Descripciones de ejemplo que funcionan bien:**

| Bastidor | Descripción de ejemplo | Resultado esperado |
|----------|----------------------|-------------------|
| `AK550-POC-0001` | "el motor se para en caliente y no arranca hasta que enfría" | Reglaje de válvulas pisado |
| `AK550-2023-0001` | "hay mucho ruido en la zona del variador cuando acelero" | Poleas del variador con desgaste / rodillos CVT |
| `XCITING-POC-0001` | "arranca pero se cala a los 2 minutos sin previo aviso" | Sensor de inclinación defectuoso |
| `CV5-POC-0001` | "el testigo de batería parpadea y pierde potencia" | Batería debilitada o regulador de carga |
| `DTXS-POC-0001` | "no da chispa, la bujía está nueva" | Bobina de encendido defectuosa |
| `AK550-POC-0002` | "sale humo negro por el escape y huele a gasolina quemada" | Mezcla rica: inyector que gotea o sensor NTC |
| `XCITING-2023-0001` | "el CELP muestra P0120 tras la revisión" | TPS fuera de rango — recalibrar acelerador |
| `AK550-POC-0003` | "gasta mucha gasolina desde que le hice el aceite" | Ralentí desajustado / depósito de carbón |

---

## 4. Panel de analítica (sidebar izquierdo)

El panel de analítica está **siempre visible** en la columna izquierda. Tiene 5 secciones desplegables:

| Sección | Datos que muestra |
|---------|------------------|
| 📊 **Métricas del sistema** | Total sesiones, tasa de éxito, pasos promedio, duración media, uso por módulo (árbol/FAQ/historial), feedback, top diagnósticos |
| 🗂️ **Sesiones recientes** | Últimas 10 sesiones con modelo, estado (active/closed), resultado y duración |
| 🔎 **Diagnósticos** | Ranking de diagnósticos más frecuentes con barra de progreso relativa |
| 💬 **Feedback** | Tasa de valoraciones positivas + lista de comentarios recibidos |
| 📚 **Base de conocimiento** | Subtabs: Árboles disponibles / FAQs (40) / Casos históricos (76) |

> Clic en el icono `◀` para contraer el panel a modo icono. Clic en cualquier icono del panel contraído para expandir directamente en esa sección.

---

## 5. Flujos de demostración recomendados

### Demo 1 — Flujo completo con árbol (5 min)
```
1. Abrir http://localhost:3000
2. Bastidor: AK550-POC-0001
3. Síntoma: 🔩 Problemas de arranque
4. Responder preguntas del árbol (aprox. 4-6 preguntas)
5. Ver diagnóstico final con confianza 90%
6. Dar feedback positivo
7. Abrir panel analítica → Métricas: ver sesión contabilizada
```

### Demo 2 — Consumo excesivo (árbol nuevo, 3 min)
```
1. Bastidor: AK550-POC-0004
2. Síntoma: ⛽ Consumo excesivo
3. Seguir árbol respondiendo según el caso a demostrar
4. Observar la barra de progreso (F4) conforme se avanza
```

### Demo 3 — Descripción libre con LLM (3 min)
```
1. Bastidor: XCITING-POC-0001
2. Opción: 💬 Describir el problema
3. Texto: "arranca bien pero a los 5 minutos el motor se para sin previo aviso"
4. Ver hipótesis generada (historial + LLM narrative)
5. Ver ruta "🔍 Historial" en la burbuja de respuesta
```

### Demo 4 — Consulta FAQ (2 min)
```
1. Bastidor: CV5-POC-0001
2. Opción: 📋 Consultas frecuentes
3. Categoría: Batería
4. Ver respuesta sobre batería CV5
```

### Demo 5 — Panel analítica completo (3 min)
```
1. Abrir panel izquierdo → 📊 Métricas
2. Expandir 🗂️ Sesiones → ver sesiones anteriores
3. Expandir 🔎 Diagnósticos → ver ranking
4. Expandir 📚 Conocimiento → subtab Árboles → ver 5 árboles activos
5. Subtab Casos → ver muestra de casos históricos (76 total)
```

---

## 6. Indicador de estado del sistema

El indicador en la esquina superior derecha muestra el estado en tiempo real:

| Estado | Color | Significado |
|--------|-------|-------------|
| 🟢 Sistema activo | Verde parpadeante | Backend OK, DB conectada |
| 🟡 Degradado | Amarillo parpadeante | Backend responde pero con errores |
| 🔴 Sin conexión | Rojo fijo | Backend no disponible |
| ⚫ Verificando | Gris parpadeante | Primera comprobación en curso |

> Se comprueba automáticamente cada 30 segundos.

---

## 7. Referencia técnica rápida

### Endpoints de la API

| Método | URL | Descripción |
|--------|-----|-------------|
| `GET`  | `/health` | Estado del sistema |
| `POST` | `/session/start` | Iniciar nueva sesión |
| `POST` | `/session/message` | Enviar mensaje |
| `GET`  | `/session/{id}` | Datos de una sesión |
| `POST` | `/session/{id}/feedback` | Registrar valoración |
| `GET`  | `/metrics/summary` | KPIs del sistema |
| `GET`  | `/analytics/sessions` | Listado de sesiones |
| `GET`  | `/analytics/diagnoses` | Ranking de diagnósticos |
| `GET`  | `/analytics/feedback` | Listado de feedback |
| `GET`  | `/knowledge/trees` | Árboles de diagnóstico |
| `GET`  | `/knowledge/faqs` | Base de FAQs |
| `GET`  | `/knowledge/cases` | Casos históricos |

### Comandos de administración

```powershell
# Estado de contenedores
docker compose ps

# Ver logs del backend en tiempo real
docker logs poc-backend -f

# Consultar base de datos directamente
docker exec poc-postgres psql -U poc_user -d poc_asistente -c "SELECT vin, model FROM vehicles ORDER BY model;"

# Recargar seeds (en caso de reinicio de DB)
Get-Content backend\db\seeds\vehicles_enrichment.sql | docker exec -i poc-postgres psql -U poc_user -d poc_asistente

# Reconstruir imágenes
docker compose up -d --build backend frontend
```

---

## 8. Datos de prueba — Resumen rápido

```
── AK550         14 VINs ── árboles: Motor / Arranque / CELP / Consumo
── AK550 Elite    5 VINs ── árboles: Motor / Arranque / CELP / Consumo
── Xciting S 400  8 VINs ── árbol:  Motor
── CV5            7 VINs ── sin árbol → FAQ + descripción libre
── DT X360        5 VINs ── sin árbol → FAQ + descripción libre
── Agility 125    5 VINs ── sin árbol → FAQ + descripción libre

── Casos históricos: 76
── FAQs:             40
── Árboles activos:   5 (total 57 nodos)
```

---

*Generado automáticamente · POC Asistente Técnico v1.0 · Mayo 2026*
