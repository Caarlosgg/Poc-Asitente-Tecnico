# Backend - Scaffolding de Arquitectura

Este modulo define unicamente la estructura base para la API y la orquestacion conversacional.

Objetivo de esta fase:

- organizar carpetas por responsabilidad,
- dejar limites modulares claros,
- evitar implementar logica de negocio prematuramente.

## Capas

- app/api: routers y schemas de entrada/salida.
- app/core: configuracion y logging.
- app/db: bootstrap de persistencia y modelos ORM futuros.
- app/modules: modulos funcionales del DDT desacoplados.
- tests: pruebas de integracion/end-to-end en fases siguientes.

## Por que hay tantos modulos ya en esta fase

Aunque parezcan muchos para una POC, es intencional y tiene sentido tecnico:

- el DDT exige separacion por responsabilidades (orquestador, FAQ, arbol, otros, ranking, etc.),
- deja claros los limites de cada componente antes de escribir logica,
- reduce riesgo de acoplamiento cuando empiece la implementacion,
- permite avanzar por sprints sin rehacer estructura de carpetas.

## Modulos previstos en app/modules

- orchestrator: decide a que flujo va cada turno.
- vin_lookup: identifica el modelo a partir del bastidor.
- session_state: persistencia del estado vivo de la sesion.
- faq_matcher: resolucion de consultas frecuentes.
- tree_engine: ejecucion de arboles de diagnostico.
- free_text_parser: normalizacion y extraccion inicial de senales de texto libre.
- historical_retrieval: recuperacion de casos similares por modelo.
- hybrid_ranking: ordena hipotesis con senales combinadas.
- response_builder: unifica el contrato de salida final.
- traceability: registro input/output de decisiones.
- feedback_metrics: almacenamiento de feedback y KPIs.

Importante: en Fase 1 estos modulos son solo contenedores de arquitectura (sin implementacion).

En esta fase no hay codigo ejecutable en backend. Solo arquitectura base.

## Reglas de evolucion escalable (backend)

- Si aparece una nueva capacidad, crear modulo nuevo en app/modules antes de mezclar logica en otro.
- Evitar dependencias cruzadas entre modulos funcionales; la coordinacion pasa por el orquestador.
- Mantener contratos de entrada/salida simples para facilitar pruebas y reemplazo de componentes.
- Cualquier cambio de esquema de datos debe entrar por migraciones incrementales, nunca por cambios manuales.
- Priorizar compatibilidad hacia atras en endpoints para no romper el frontend al evolucionar.