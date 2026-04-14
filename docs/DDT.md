**Documento de Diseño Técnico (DDT)  
POC - Asistente Conversacional de Diagnóstico por Bastidor**

Versión 1.0  
Documento para el equipo de desarrollo

| **Proyecto**  | POC de asistente técnico con lógica híbrida: bastidor + árbol + FAQ + casos históricos + IA.                                                                        |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Objetivo**  | Guiar al equipo de desarrollo para implementar una POC completa, trazable y evaluable.                                                                              |
| **Alcance**   | Incluye arquitectura funcional y técnica, módulos, datos mock, tablas SQL, endpoints, reglas de negocio, flujos, criterios de aceptación y backlog técnico inicial. |
| **Audiencia** | Backend, frontend, IA/aplicación, QA y responsables de producto.                                                                                                    |

# 1\. Contexto

Se va a desarrollar una POC de un asistente conversacional orientado a diagnóstico técnico de motocicletas. El sistema debe arrancar siempre desde la identificación del vehículo por bastidor y, a partir de ahí, contextualizar la conversación en función del modelo identificado.

La hipótesis de producto a validar es que un sistema híbrido -basado en reglas, árboles estructurados, FAQs, búsqueda de casos históricos y un componente de IA para entrada libre- ofrece una experiencia más útil, controlable y escalable que un chatbot puramente generativo.

La POC no pretende cubrir el producto final. Pretende validar los componentes esenciales de la solución, demostrar viabilidad técnica y preparar una base limpia para evolucionar a MVP.

# 2\. Objetivos de la POC

- Validar el flujo obligatorio de identificación por bastidor.
- Validar la navegación por síntomas conocidos y la ejecución de un árbol de diagnóstico real.
- Validar una vía de entrada libre ("Otros") con clasificación, búsqueda y ranking.
- Validar una base de FAQs como resolución rápida de dudas frecuentes.
- Validar persistencia de contexto y trazabilidad completa de sesiones.
- Validar métricas mínimas para evaluar el uso y la utilidad de la POC.

# 3\. Alcance y límites

La POC incluye un subconjunto controlado de modelos, bastidores mock, síntomas y casos históricos. Se diseñará para ser funcional, demostrable y medible, sin incorporar todavía integraciones corporativas ni complejidad de producción.

| **Incluido en POC**                    | **Fuera de alcance**                                |
| -------------------------------------- | --------------------------------------------------- |
| Identificación por bastidor mock       | Integración con sistema real de VIN/bastidor        |
| Menú de síntomas y FAQs                | Panel de administración de contenidos               |
| Árbol completo de Paradas de motor     | Cobertura de todos los síntomas del negocio         |
| Flujo simplificado de Testigo CELP     | Diagnóstico profundo de todas las variantes de CELP |
| Entrada libre "Otros" con IA y ranking | Modelos avanzados de ML o aprendizaje online        |
| Persistencia de contexto y logs        | Multiusuario con autenticación y permisos           |
| Métricas básicas y feedback            | BI avanzada / dashboards corporativos               |

# 4\. Principios de diseño

- El bastidor es obligatorio: no se continúa sin vehículo identificado.
- El modelo se obtiene del sistema, no se infiere solo del texto del usuario.
- El estado de sesión es la fuente de verdad; el LLM no es la memoria del sistema.
- El LLM no decide solo el diagnóstico; apoya en comprensión, clasificación y redacción.
- Toda decisión relevante debe ser trazable.
- Las respuestas del asistente deben tener un formato estándar.
- La POC debe ser simple de construir, pero suficientemente modular para escalar a MVP.

# 5\. Flujo general del sistema

- Usuario inicia conversación.
- Asistente solicita bastidor.
- Usuario introduce bastidor.
- Sistema valida bastidor y obtiene modelo.
- Sistema ofrece menú principal: Síntomas frecuentes, Consultas frecuentes (FAQ) y Otros.
- Usuario elige una vía de entrada.
- Orquestador decide el módulo a ejecutar (FAQ, árbol o entrada libre).
- Sistema genera respuesta estructurada y actualiza el estado de sesión.
- Se registra trazabilidad del turno.
- Al finalizar, se solicita feedback.

# 6\. Arquitectura funcional

La solución se organiza en módulos funcionales con responsabilidades separadas. Esta separación es obligatoria en la implementación, aunque en la POC se despliegue como un monolito modular.

| **Módulo**             | **Responsabilidad principal**           | **Entradas**                | **Salidas**                  |
| ---------------------- | --------------------------------------- | --------------------------- | ---------------------------- |
| Canal conversacional   | Recibir y mostrar mensajes              | Texto usuario, selecciones  | Mensajes, menús, resultados  |
| Orquestador            | Controlar flujo y enrutamiento          | Mensaje, estado             | Siguiente acción/módulo      |
| Lookup de bastidor     | Identificar vehículo                    | VIN/bastidor                | Modelo/familia/año/mercado   |
| Estado de sesión       | Persistir contexto vivo                 | Cambios de conversación     | Estado actualizado           |
| FAQ matcher            | Resolver preguntas frecuentes           | Modelo + texto/categoría    | FAQ o no match               |
| Motor de árbol         | Ejecutar árbol estructurado             | Nodo actual + respuesta     | Nueva pregunta o diagnóstico |
| Parser de texto libre  | Extraer estructura del lenguaje natural | Texto libre + modelo        | Tags/categoría/atributos     |
| Búsqueda en históricos | Recuperar casos similares               | Modelo + texto/tags         | Casos candidatos             |
| Ranking híbrido        | Ordenar hipótesis                       | Candidatos + señales        | Top-1 / Top-3                |
| Generador de respuesta | Construir salida visible                | Resultado técnico           | Respuesta estándar           |
| Trazabilidad           | Registrar decisiones                    | Entradas/salidas por módulo | Logs persistidos             |
| Métricas y feedback    | Medir utilidad y uso                    | Sesiones + feedback         | Indicadores básicos          |

# 7\. Arquitectura técnica

La POC se implementará como un monolito modular. La decisión es deliberada: reduce complejidad operativa, acelera el desarrollo y es suficiente para validar la solución.

| **Capa**                | **Tecnología recomendada**      | **Motivo**                                         |
| ----------------------- | ------------------------------- | -------------------------------------------------- |
| Frontend                | React o Next.js                 | UI simple de chat con botones / quick replies      |
| Backend                 | Python + FastAPI                | Rapidez de desarrollo e integración con IA         |
| Orquestación            | LangGraph                       | Control de flujo y estado conversacional           |
| Base de datos principal | PostgreSQL                      | Robusta, simple y reutilizable                     |
| Búsqueda vectorial      | pgvector                        | Permite búsqueda semántica sin otra base adicional |
| Persistencia de árboles | JSON versionado + tabla SQL     | Mantenible y fácil de editar                       |
| Proveedor LLM           | Un único proveedor configurable | Reducir complejidad en POC                         |

# 8\. Menú principal después del bastidor

Una vez identificado el modelo, el sistema debe mostrar un menú principal claro. Es importante separar "síntomas frecuentes" de "consultas frecuentes" para evitar ambigüedad.

| **Bloque**           | **Opciones POC**                                 |
| -------------------- | ------------------------------------------------ |
| Síntomas frecuentes  | Paradas de motor; Testigo CELP encendido         |
| Consultas frecuentes | FAQs específicas del modelo y FAQs generales     |
| Entrada libre        | Otros (texto libre; opcionalmente voz en futuro) |

# 9\. Definición exacta de la opción "Otros"

"Otros" no es un chat genérico. Es una vía de entrada libre en la que el usuario describe el problema con sus palabras. El sistema debe interpretar el texto, filtrar por modelo, buscar casos históricos similares y, cuando sea posible, reconducir al usuario a un flujo guiado.

En la POC, "Otros" buscará en tres fuentes, en este orden lógico: (1) casos históricos del mismo modelo, (2) FAQs del mismo modelo o generales y (3) catálogo de síntomas conocidos para intentar clasificar o reconducir a un árbol.

| **Paso**          | **Descripción**                                                         |
| ----------------- | ----------------------------------------------------------------------- |
| 1\. Normalización | Pasar a minúsculas, limpiar puntuación básica, eliminar ruido textual.  |
| 2\. Extracción    | Generar tags/atributos a partir del texto (reglas simples o apoyo LLM). |
| 3\. Filtrado      | Reducir candidatos al modelo identificado por bastidor.                 |
| 4\. Recuperación  | Buscar casos históricos similares y FAQs relacionadas.                  |
| 5\. Ranking       | Ordenar hipótesis con score híbrido.                                    |
| 6\. Respuesta     | Devolver hipótesis probables y siguiente comprobación.                  |
| 7\. Reconducción  | Si procede, redirigir al flujo estructurado más adecuado.               |

# 10\. Requisitos funcionales

- RF-001 El sistema debe solicitar bastidor al inicio de toda sesión.
- RF-002 El sistema debe validar si el bastidor existe en la base mock.
- RF-003 El sistema debe obtener el modelo del bastidor validado.
- RF-004 El sistema debe persistir una sesión con identificador único.
- RF-005 El sistema debe mostrar menú principal tras la identificación del modelo.
- RF-006 El sistema debe permitir elegir entre síntomas frecuentes, FAQs y Otros.
- RF-007 El sistema debe ejecutar el árbol de "Paradas de motor".
- RF-008 El sistema debe ejecutar un flujo simplificado de "Testigo CELP encendido".
- RF-009 El sistema debe aceptar texto libre en "Otros".
- RF-010 El sistema debe buscar casos históricos del mismo modelo.
- RF-011 El sistema debe consultar FAQs si hay coincidencia suficiente.
- RF-012 El sistema debe devolver top-3 hipótesis en "Otros".
- RF-013 El sistema debe mantener contexto entre turnos.
- RF-014 El sistema debe evitar repetir preguntas ya respondidas.
- RF-015 El sistema debe registrar todos los mensajes.
- RF-016 El sistema debe registrar todas las decisiones del sistema.
- RF-017 El sistema debe solicitar feedback al finalizar.
- RF-018 El sistema debe permitir consultar métricas básicas.
- RF-019 El sistema debe manejar ramas fuera de alcance con respuesta controlada.
- RF-020 El sistema debe devolver una salida estándar en toda respuesta final de diagnóstico.

# 11\. Requisitos no funcionales

- RNF-001 El sistema debe ser trazable extremo a extremo.
- RNF-002 El sistema debe ser modular y mantenible.
- RNF-003 El sistema debe usar el estado estructurado como fuente de verdad.
- RNF-004 El tiempo de respuesta debe ser razonable para una demo operativa.
- RNF-005 El sistema debe tolerar errores de input sin romper la conversación.
- RNF-006 La lógica debe poder ampliarse a más modelos y síntomas sin reescritura completa.

# 12\. Diseño del estado de sesión

El contexto debe mantenerse en base de datos, no solo en memoria del LLM. Se distinguen tres niveles de contexto: contexto de sesión, contexto diagnóstico y contexto conversacional corto para el LLM.

| **Tipo de contexto**    | **Contenido**                                                                   |
| ----------------------- | ------------------------------------------------------------------------------- |
| Sesión                  | session_id, bastidor, modelo, entry_point, síntoma actual, nodo actual.         |
| Diagnóstico             | Hechos confirmados, pruebas realizadas, hipótesis activas, preguntas ya hechas. |
| Contexto corto para LLM | Resumen compacto del estado actual para redactar o clasificar.                  |

Ejemplo de state_json esperado:

{

"facts": {

"restarts_without_key_cycle": false,

"restarts_after_key_cycle": false,

"fuel_pump_audible": true,

"celp_on": false,

"improves_when_cold": true

},

"active_hypotheses": \[{"label":"Reglaje de válvulas pisado","score":0.81}\],

"asked_questions": \["n1","n3","n5","n6"\]

}

# 13\. Modelo de datos SQL

Las siguientes tablas son obligatorias para la POC.

## 13.1 vehicles

CREATE TABLE vehicles (  
vin VARCHAR(50) PRIMARY KEY,  
model VARCHAR(100) NOT NULL,  
family VARCHAR(100),  
displacement_cc INTEGER,  
market VARCHAR(20),  
model_year INTEGER,  
created_at TIMESTAMP NOT NULL DEFAULT NOW()  
);

## 13.2 faqs

CREATE TABLE faqs (  
faq_id SERIAL PRIMARY KEY,  
model VARCHAR(100),  
category VARCHAR(100),  
question TEXT NOT NULL,  
answer TEXT NOT NULL,  
usage_count INTEGER NOT NULL DEFAULT 0,  
active BOOLEAN NOT NULL DEFAULT TRUE,  
created_at TIMESTAMP NOT NULL DEFAULT NOW(),  
updated_at TIMESTAMP NOT NULL DEFAULT NOW()  
);

## 13.3 diagnostic_trees

CREATE TABLE diagnostic_trees (  
tree_id VARCHAR(100) PRIMARY KEY,  
model VARCHAR(100),  
symptom VARCHAR(100) NOT NULL,  
version INTEGER NOT NULL DEFAULT 1,  
tree_json JSONB NOT NULL,  
active BOOLEAN NOT NULL DEFAULT TRUE,  
created_at TIMESTAMP NOT NULL DEFAULT NOW(),  
updated_at TIMESTAMP NOT NULL DEFAULT NOW()  
);

## 13.4 historical_cases

CREATE TABLE historical_cases (  
case_id VARCHAR(50) PRIMARY KEY,  
model VARCHAR(100) NOT NULL,  
symptom_category VARCHAR(100),  
case_text TEXT NOT NULL,  
final_diagnosis VARCHAR(255) NOT NULL,  
base_confidence NUMERIC(5,4) NOT NULL,  
created_at TIMESTAMP NOT NULL DEFAULT NOW()  
);

## 13.5 sessions

CREATE TABLE sessions (  
session_id UUID PRIMARY KEY,  
vin VARCHAR(50),  
model VARCHAR(100),  
entry_point VARCHAR(50),  
status VARCHAR(50) NOT NULL DEFAULT 'active',  
started_at TIMESTAMP NOT NULL DEFAULT NOW(),  
ended_at TIMESTAMP,  
total_steps INTEGER NOT NULL DEFAULT 0,  
final_result VARCHAR(255),  
success BOOLEAN,  
FOREIGN KEY (vin) REFERENCES vehicles(vin)  
);

## 13.6 session_state

CREATE TABLE session_state (  
session_id UUID PRIMARY KEY,  
vin VARCHAR(50),  
model VARCHAR(100),  
current_symptom VARCHAR(100),  
current_node VARCHAR(100),  
state_json JSONB NOT NULL DEFAULT '{}'::jsonb,  
updated_at TIMESTAMP NOT NULL DEFAULT NOW(),  
FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,  
FOREIGN KEY (vin) REFERENCES vehicles(vin)  
);

## 13.7 messages

CREATE TABLE messages (  
message_id BIGSERIAL PRIMARY KEY,  
session_id UUID NOT NULL,  
role VARCHAR(20) NOT NULL,  
content TEXT NOT NULL,  
created_at TIMESTAMP NOT NULL DEFAULT NOW(),  
FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE  
);

## 13.8 decision_logs

CREATE TABLE decision_logs (  
log_id BIGSERIAL PRIMARY KEY,  
session_id UUID NOT NULL,  
module_name VARCHAR(100) NOT NULL,  
input_data JSONB,  
output_data JSONB,  
created_at TIMESTAMP NOT NULL DEFAULT NOW(),  
FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE  
);

## 13.9 feedback

CREATE TABLE feedback (  
feedback_id BIGSERIAL PRIMARY KEY,  
session_id UUID NOT NULL UNIQUE,  
useful BOOLEAN NOT NULL,  
comment TEXT,  
created_at TIMESTAMP NOT NULL DEFAULT NOW(),  
FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE  
);

# 14\. Índices recomendados

CREATE INDEX idx_sessions_vin ON sessions(vin);  
CREATE INDEX idx_sessions_model ON sessions(model);  
CREATE INDEX idx_messages_session_id ON messages(session_id);  
CREATE INDEX idx_decision_logs_session_id ON decision_logs(session_id);  
CREATE INDEX idx_session_state_model ON session_state(model);  
CREATE INDEX idx_historical_cases_model ON historical_cases(model);  
CREATE INDEX idx_historical_cases_symptom_category ON historical_cases(symptom_category);  
CREATE INDEX idx_faqs_model ON faqs(model);  
CREATE INDEX idx_faqs_category ON faqs(category);

# 15\. Datos mock de la POC

La POC debe incluir datos inventados suficientes para probar el flujo. Se recomiendan al menos cuatro bastidores, cuatro FAQs, un árbol completo de Paradas de motor y cinco casos históricos.

| **Dataset**      | **Mínimo recomendado**                  |
| ---------------- | --------------------------------------- |
| Vehicles         | 4 bastidores mock                       |
| FAQs             | 4 registros                             |
| Diagnostic trees | 1 árbol completo + 1 flujo simplificado |
| Historical cases | 5 casos para AK550                      |

- Ejemplos de bastidores mock:
- AK550-POC-0001
- AK550-POC-0002
- AK550-POC-0003
- XCITING-POC-0001

# 16\. Árbol de diagnóstico base - Paradas de motor

El árbol obligatorio en la POC será "Paradas de motor". Debe persistirse en JSON y ejecutarse a través del motor de árbol.

{  
"start_node": "n1",  
"nodes": {  
"n1": {"type":"question","text":"Cuando se para, ¿arranca sin quitar contacto?","answers":{"si":"n2","no":"n3"}},  
"n2": {"type":"diagnosis","result":"Mal contacto en pipa de bujía"},  
"n3": {"type":"question","text":"Quita contacto y vuelve a intentar. ¿Arranca?","answers":{"si":"n4","no":"n5"}},  
"n4": {"type":"diagnosis","result":"Sensor de inclinación defectuoso"},  
"n5": {"type":"question","text":"¿Se escucha la bomba de gasolina?","answers":{"si":"n6","no":"n7"}},  
"n7": {"type":"diagnosis","result":"Bomba de gasolina defectuosa"},  
"n6": {"type":"question","text":"¿Arranca después de enfriar?","answers":{"si":"n8","no":"n9"}},  
"n8": {"type":"diagnosis","result":"Reglaje de válvulas pisado"},  
"n9": {"type":"diagnosis","result":"Agua en el depósito"}  
}  
}

# 17\. Reglas de negocio y enrutamiento

- RN-NEG-001 Sin bastidor válido, la sesión no puede entrar en diagnóstico.
- RN-NEG-002 Una vez identificado el bastidor, el modelo queda fijado en la sesión.
- RN-NEG-003 Si el usuario elige un síntoma conocido, se prioriza el árbol.
- RN-NEG-004 Si la consulta textual encaja claramente con una FAQ, se responde por FAQ.
- RN-NEG-005 Si la consulta es libre y no resuelve por FAQ, se usa el flujo "Otros".
- RN-NEG-006 En "Otros", los históricos se filtran por modelo antes del ranking.
- RN-NEG-007 Si una rama está fuera de alcance, el sistema debe responder de forma controlada.
- RN-NEG-008 Toda respuesta final debe ajustarse al contrato de salida estándar.

# 18\. Contrato de salida estándar

Toda respuesta final de diagnóstico debe seguir el mismo formato lógico, independientemente del módulo que la haya generado.

{  
"primary_hypothesis": "Reglaje de válvulas pisado",  
"alternatives": \["Bomba de gasolina defectuosa", "Sensor de inclinación defectuoso"\],  
"next_check": "Verificar reglaje de válvulas",  
"short_explanation": "La moto falla en caliente y vuelve a arrancar al enfriar, patrón compatible con pérdida de compresión en caliente.",  
"confidence": 0.81  
}

# 19\. Diseño del módulo "Otros"

El objetivo del módulo es traducir una descripción libre del usuario a una hipótesis técnica útil y, cuando sea posible, reconducir el caso a un flujo estructurado.

- Recibir texto libre y asociarlo a la sesión actual.
- Normalizar el texto (minúsculas, limpieza básica, ruido mínimo).
- Extraer tags y atributos (por reglas simples o apoyo LLM).
- Filtrar históricos por modelo identificado en la sesión.
- Buscar coincidencias en históricos y FAQs.
- Calcular ranking híbrido.
- Seleccionar top-3 hipótesis.
- Construir una respuesta con siguiente comprobación.
- Si procede, sugerir la categoría o flujo conocido al que reconducir.

Señales mínimas de ranking:

- similitud del texto con casos históricos
- coincidencia de modelo
- frecuencia histórica
- base_confidence del caso

# 20\. Endpoints requeridos

| **Endpoint**           | **Método** | **Descripción**                                 |
| ---------------------- | ---------- | ----------------------------------------------- |
| /session/start         | POST       | Inicia una sesión y devuelve el primer mensaje. |
| /session/message       | POST       | Procesa un turno de conversación.               |
| /session/{id}          | GET        | Consulta sesión y estado actual.                |
| /session/{id}/feedback | POST       | Guarda feedback final de sesión.                |
| /metrics/summary       | GET        | Devuelve métricas internas básicas.             |

## 20.1 Ejemplo /session/start

Request:  
{}  
<br/>Response:  
{  
"session_id": "uuid",  
"message": "Hola. Indícame el bastidor para identificar el vehículo y ayudarte con el diagnóstico."  
}

## 20.2 Ejemplo /session/message

Request:  
{  
"session_id": "uuid",  
"message": "AK550-POC-0002"  
}  
<br/>Response:  
{  
"session_id": "uuid",  
"message": "He identificado el vehículo como AK550 (2022). Selecciona una opción: Síntomas frecuentes, Consultas frecuentes u Otros.",  
"state": {  
"vin": "AK550-POC-0002",  
"model": "AK550",  
"current_symptom": null,  
"current_node": null  
}  
}

# 21\. Trazabilidad obligatoria

Cada módulo crítico debe registrar entradas y salidas. El objetivo es poder reconstruir cada decisión y depurar el sistema.

| **Campo**   | **Descripción**                                                                                                                  |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------- |
| session_id  | Identificador de sesión                                                                                                          |
| module_name | Módulo ejecutado: vin_lookup, faq_matcher, tree_engine, free_text_parser, historical_retrieval, hybrid_ranking, response_builder |
| input_data  | Entrada al módulo                                                                                                                |
| output_data | Salida del módulo                                                                                                                |
| created_at  | Timestamp de ejecución                                                                                                           |

# 22\. Métricas mínimas

- número total de sesiones
- sesiones finalizadas
- tiempo medio por sesión
- pasos medios por sesión
- uso de FAQ
- uso de árbol
- uso de Otros
- final_result más frecuente
- feedback positivo vs negativo

# 23\. Casos de error y edge cases

| **Escenario**                          | **Comportamiento esperado**                            |
| -------------------------------------- | ------------------------------------------------------ |
| Bastidor inexistente                   | Mensaje claro de no identificación; no se continúa.    |
| Usuario no elige una opción válida     | Mensaje de reintento con opciones disponibles.         |
| Rama no implementada                   | Mensaje controlado: fuera de alcance de la POC.        |
| No hay casos históricos suficientes    | Devolver lo mejor disponible y declarar incertidumbre. |
| Error temporal del LLM                 | Fallback a reglas / mensaje de reintento.              |
| Respuesta ambigua del usuario en árbol | Repregunta o normalización a sí/no si es posible.      |

# 24\. Criterios de aceptación

- CA-001 Identifica correctamente todos los bastidores mock cargados.
- CA-002 No permite continuar sin bastidor válido.
- CA-003 Mantiene modelo, síntoma y nodo actual en session_state.
- CA-004 Ejecuta correctamente el árbol de Paradas de motor.
- CA-005 Resuelve FAQ cuando la consulta encaja.
- CA-006 El flujo Otros devuelve top-3 hipótesis con el modelo correcto.
- CA-007 Toda sesión genera messages y decision_logs.
- CA-008 Se registra feedback y métricas básicas.
- CA-009 La salida final sigue el contrato estándar.
- CA-010 El sistema maneja fuera de alcance sin romper la conversación.

# 25\. Orden de implementación recomendado

- Crear esquema SQL y cargar mock data.
- Implementar /session/start y /session/message.
- Implementar lookup de bastidor.
- Implementar session_state y messages.
- Implementar menú principal.
- Implementar motor de árbol para Paradas de motor.
- Implementar FAQs.
- Implementar decision_logs.
- Implementar flujo Otros con recuperación y ranking.
- Implementar feedback y métricas.
- Cubrir casos de error y pruebas end-to-end.

# 26\. Backlog técnico inicial

| **ID** | **Tarea**                            | **Prioridad** |
| ------ | ------------------------------------ | ------------- |
| BE-01  | Migraciones SQL iniciales            | Alta          |
| BE-02  | Seed de datos mock                   | Alta          |
| BE-03  | Endpoint /session/start              | Alta          |
| BE-04  | Endpoint /session/message            | Alta          |
| BE-05  | Lookup bastidor + creación de sesión | Alta          |
| BE-06  | Persistencia de session_state        | Alta          |
| BE-07  | Motor de árbol Paradas de motor      | Alta          |
| BE-08  | Motor de FAQ                         | Media         |
| BE-09  | Parser de texto libre + etiquetas    | Media         |
| BE-10  | Recuperación en historical_cases     | Media         |
| BE-11  | Ranking híbrido                      | Media         |
| BE-12  | Feedback + métricas                  | Media         |
| FE-01  | UI de chat                           | Alta          |
| FE-02  | Quick replies / menús                | Alta          |
| FE-03  | Vista de resultado estándar          | Alta          |
| QA-01  | Casos de prueba end-to-end           | Alta          |

# 27\. Observaciones finales

Esta POC debe verse como una base controlada para validar producto y arquitectura. La intención no es crear un chatbot libre, sino un sistema de diagnóstico técnico con interfaz conversacional.

Las decisiones aquí descritas deben respetarse en desarrollo para no desvirtuar la validación: el bastidor es obligatorio, el contexto vive en base de datos, y la IA es un apoyo del sistema, no su única lógica.

Una vez superada la POC, el siguiente paso natural es pasar a MVP añadiendo más modelos, más síntomas, mejor recuperación semántica y un sistema de evaluación continua más robusto.

Anexos

**1\. Dataset vehicles**

**SQL**

INSERT INTO vehicles (vin, model, family, displacement_cc, market, model_year)  
VALUES  
('AK550-POC-0001', 'AK550', 'Scooter GT', 550, 'ES', 2022),  
('AK550-POC-0002', 'AK550', 'Scooter GT', 550, 'ES', 2023),  
('AK550-POC-0003', 'AK550', 'Scooter GT', 550, 'ES', 2024),  
('XCITING-POC-0001', 'Xciting 400', 'Scooter GT', 400, 'ES', 2021);

**JSON equivalente**

\[  
{  
"vin": "AK550-POC-0001",  
"model": "AK550",  
"family": "Scooter GT",  
"displacement_cc": 550,  
"market": "ES",  
"model_year": 2022  
},  
{  
"vin": "AK550-POC-0002",  
"model": "AK550",  
"family": "Scooter GT",  
"displacement_cc": 550,  
"market": "ES",  
"model_year": 2023  
},  
{  
"vin": "AK550-POC-0003",  
"model": "AK550",  
"family": "Scooter GT",  
"displacement_cc": 550,  
"market": "ES",  
"model_year": 2024  
},  
{  
"vin": "XCITING-POC-0001",  
"model": "Xciting 400",  
"family": "Scooter GT",  
"displacement_cc": 400,  
"market": "ES",  
"model_year": 2021  
}  
\]

**2\. Dataset faqs**

**SQL**

INSERT INTO faqs (model, category, question, answer, usage_count, active)  
VALUES  
(  
'AK550',  
'Paradas de motor',  
'¿Por qué puede pararse la moto en marcha de forma intermitente?',  
'Las causas más probables en esta POC son: sensor de inclinación defectuoso, bomba de gasolina defectuosa, reglaje de válvulas pisado, agua en el depósito o mal contacto en pipa de bujía.',  
0,  
TRUE  
),  
(  
'AK550',  
'Combustible',  
'¿Qué significa que no se escuche la bomba de gasolina al dar contacto?',  
'En esta POC se interpreta como una señal compatible con fallo de bomba de gasolina o falta de alimentación eléctrica al sistema de combustible.',  
0,  
TRUE  
),  
(  
NULL,  
'General',  
'¿Qué significa el testigo CELP encendido?',  
'En esta POC, el testigo CELP indica una avería relacionada con la gestión electrónica del motor o el sistema de inyección y debe orientar la diagnosis hacia la rama específica de CELP.',  
0,  
TRUE  
),  
(  
'AK550',  
'Mantenimiento',  
'¿Qué puede indicar que falle en caliente y vuelva a arrancar en frío?',  
'En esta POC, ese patrón es compatible con reglaje de válvulas pisado y pérdida de compresión en caliente.',  
0,  
TRUE  
);

**JSON equivalente**

\[  
{  
"model": "AK550",  
"category": "Paradas de motor",  
"question": "¿Por qué puede pararse la moto en marcha de forma intermitente?",  
"answer": "Las causas más probables en esta POC son: sensor de inclinación defectuoso, bomba de gasolina defectuosa, reglaje de válvulas pisado, agua en el depósito o mal contacto en pipa de bujía.",  
"usage_count": 0,  
"active": true  
},  
{  
"model": "AK550",  
"category": "Combustible",  
"question": "¿Qué significa que no se escuche la bomba de gasolina al dar contacto?",  
"answer": "En esta POC se interpreta como una señal compatible con fallo de bomba de gasolina o falta de alimentación eléctrica al sistema de combustible.",  
"usage_count": 0,  
"active": true  
},  
{  
"model": null,  
"category": "General",  
"question": "¿Qué significa el testigo CELP encendido?",  
"answer": "En esta POC, el testigo CELP indica una avería relacionada con la gestión electrónica del motor o el sistema de inyección y debe orientar la diagnosis hacia la rama específica de CELP.",  
"usage_count": 0,  
"active": true  
},  
{  
"model": "AK550",  
"category": "Mantenimiento",  
"question": "¿Qué puede indicar que falle en caliente y vuelva a arrancar en frío?",  
"answer": "En esta POC, ese patrón es compatible con reglaje de válvulas pisado y pérdida de compresión en caliente.",  
"usage_count": 0,  
"active": true  
}  
\]

**3\. Dataset historical_cases**

**SQL**

INSERT INTO historical_cases (case_id, model, symptom_category, case_text, final_diagnosis, base_confidence)  
VALUES  
(  
'CASE-001',  
'AK550',  
'Paradas de motor',  
'La moto se para en marcha al pasar por baches y vuelve a arrancar después de quitar y dar contacto.',  
'Sensor de inclinación defectuoso',  
0.8500  
),  
(  
'CASE-002',  
'AK550',  
'Paradas de motor',  
'La moto se para y al volver a dar contacto no se escucha la bomba de gasolina.',  
'Bomba de gasolina defectuosa',  
0.9000  
),  
(  
'CASE-003',  
'AK550',  
'Paradas de motor',  
'La moto se para en caliente y después de enfriar vuelve a arrancar con normalidad.',  
'Reglaje de válvulas pisado',  
0.8800  
),  
(  
'CASE-004',  
'AK550',  
'Paradas de motor',  
'Tras repostar, la moto presenta paradas intermitentes y funcionamiento irregular.',  
'Agua en el depósito',  
0.7500  
),  
(  
'CASE-005',  
'AK550',  
'Paradas de motor',  
'La moto se para de forma intermitente pero a veces rearranca sin necesidad de quitar contacto.',  
'Mal contacto en pipa de bujía',  
0.7000  
);

**JSON equivalente**

\[  
{  
"case_id": "CASE-001",  
"model": "AK550",  
"symptom_category": "Paradas de motor",  
"case_text": "La moto se para en marcha al pasar por baches y vuelve a arrancar después de quitar y dar contacto.",  
"final_diagnosis": "Sensor de inclinación defectuoso",  
"base_confidence": 0.85  
},  
{  
"case_id": "CASE-002",  
"model": "AK550",  
"symptom_category": "Paradas de motor",  
"case_text": "La moto se para y al volver a dar contacto no se escucha la bomba de gasolina.",  
"final_diagnosis": "Bomba de gasolina defectuosa",  
"base_confidence": 0.9  
},  
{  
"case_id": "CASE-003",  
"model": "AK550",  
"symptom_category": "Paradas de motor",  
"case_text": "La moto se para en caliente y después de enfriar vuelve a arrancar con normalidad.",  
"final_diagnosis": "Reglaje de válvulas pisado",  
"base_confidence": 0.88  
},  
{  
"case_id": "CASE-004",  
"model": "AK550",  
"symptom_category": "Paradas de motor",  
"case_text": "Tras repostar, la moto presenta paradas intermitentes y funcionamiento irregular.",  
"final_diagnosis": "Agua en el depósito",  
"base_confidence": 0.75  
},  
{  
"case_id": "CASE-005",  
"model": "AK550",  
"symptom_category": "Paradas de motor",  
"case_text": "La moto se para de forma intermitente pero a veces rearranca sin necesidad de quitar contacto.",  
"final_diagnosis": "Mal contacto en pipa de bujía",  
"base_confidence": 0.7  
}  
\]

**4\. Flujo simplificado diagnostic_trees para "Testigo CELP encendido"**

"1 árbol completo + 1 flujo simplificado"

**SQL**

INSERT INTO diagnostic_trees (tree_id, model, symptom, version, tree_json, active)  
VALUES (  
'AK550_CELP_V1',  
'AK550',  
'Testigo CELP encendido',  
1,  
'{  
"start_node": "c1",  
"nodes": {  
"c1": {  
"type": "question",  
"text": "¿La moto arranca y funciona, aunque con el testigo CELP encendido?",  
"answers": {  
"si": "c2",  
"no": "c3"  
}  
},  
"c2": {  
"type": "diagnosis",  
"result": "Fallo electrónico no bloqueante; revisar sensor TPS, sensor de temperatura o lectura de códigos"  
},  
"c3": {  
"type": "question",  
"text": "¿Además del testigo CELP, hay dificultad de arranque o parada del motor?",  
"answers": {  
"si": "c4",  
"no": "c5"  
}  
},  
"c4": {  
"type": "diagnosis",  
"result": "Posible fallo de alimentación o gestión electrónica del combustible"  
},  
"c5": {  
"type": "diagnosis",  
"result": "Revisar lectura de códigos y comprobaciones eléctricas básicas"  
}  
}  
}'::jsonb,  
TRUE  
);

**JSON equivalente**

{  
"tree_id": "AK550_CELP_V1",  
"model": "AK550",  
"symptom": "Testigo CELP encendido",  
"version": 1,  
"active": true,  
"tree_json": {  
"start_node": "c1",  
"nodes": {  
"c1": {  
"type": "question",  
"text": "¿La moto arranca y funciona, aunque con el testigo CELP encendido?",  
"answers": {  
"si": "c2",  
"no": "c3"  
}  
},  
"c2": {  
"type": "diagnosis",  
"result": "Fallo electrónico no bloqueante; revisar sensor TPS, sensor de temperatura o lectura de códigos"  
},  
"c3": {  
"type": "question",  
"text": "¿Además del testigo CELP, hay dificultad de arranque o parada del motor?",  
"answers": {  
"si": "c4",  
"no": "c5"  
}  
},  
"c4": {  
"type": "diagnosis",  
"result": "Posible fallo de alimentación o gestión electrónica del combustible"  
},  
"c5": {  
"type": "diagnosis",  
"result": "Revisar lectura de códigos y comprobaciones eléctricas básicas"  
}  
}  
}  
}