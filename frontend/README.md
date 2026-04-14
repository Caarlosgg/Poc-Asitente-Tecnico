# Frontend - Scaffolding de Arquitectura

Este modulo contiene unicamente la estructura de carpetas del frontend para la POC.

Principios de esta fase:

- definir organizacion de UI,
- evitar implementacion funcional prematura,
- comunicar claramente que se construira en fases siguientes.

## Estructura interna

- app/: composicion de paginas y layout del chat.
- components/chat/: componentes visuales del canal conversacional.
- lib/: tipos y utilidades para consumir API.
- public/: recursos estaticos.

## Por que no hay codigo funcional aun

Esta fase es solo de preparacion arquitectonica. El frontend se deja sin implementacion
para evitar introducir logica de negocio antes de cerrar contratos de API y modelo de estado.

## Reglas de evolucion escalable (frontend)

- Separar componentes de presentacion de la logica de consumo de API.
- Reutilizar componentes en components/chat antes de duplicar UI en paginas.
- Evitar acoplar textos/reglas de negocio al componente visual.
- Centralizar tipos y contratos de datos en lib para facilitar cambios de backend.
- Diseñar con capacidad de crecimiento: nuevas rutas o pasos de chat sin rehacer estructura base.
