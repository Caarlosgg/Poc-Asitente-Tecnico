/**
 * Constantes de tipos de mensaje del backend.
 * Determina qué componente renderizar en el chat.
 */

export const MESSAGE_TYPES = {
  /** Mensaje de texto plano del asistente */
  TEXT: 'text',
  /** Menú de opciones principales */
  MENU: 'menu',
  /** Pregunta con botones Sí/No */
  QUESTION: 'question',
  /** Resultado de diagnóstico con hipótesis */
  DIAGNOSIS: 'diagnosis',
  /** Mensaje de error controlado */
  ERROR: 'error',
}

/** Roles de los mensajes en el historial */
export const ROLES = {
  USER: 'user',
  ASSISTANT: 'assistant',
}
