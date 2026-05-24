/**
 * Servicio de comunicación con el backend REST.
 * Usa VITE_API_URL como base URL (configurable por entorno).
 */

const BASE_URL = import.meta.env.VITE_API_URL || ''

/**
 * Helper genérico para fetch con manejo de errores.
 * @param {string} path - Ruta relativa al BASE_URL
 * @param {RequestInit} options - Opciones de fetch
 * @returns {Promise<any>} JSON parseado de la respuesta
 */
async function apiFetch(path, options = {}) {
  const url = `${BASE_URL}${path}`
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  })

  if (!response.ok) {
    let errorDetail = `Error ${response.status}`
    try {
      const body = await response.json()
      errorDetail = body.detail || errorDetail
    } catch (_) {
      // Ignorar error de parseo
    }
    throw new Error(errorDetail)
  }

  return response.json()
}

/**
 * Inicia una nueva sesión conversacional.
 * @returns {Promise<{session_id: string, message: string, message_type: string, options: Array|null}>}
 */
export async function startSession() {
  return apiFetch('/session/start', { method: 'POST' })
}

/**
 * Envía un mensaje del usuario al backend.
 * @param {string} sessionId - UUID de la sesión
 * @param {string} message - Mensaje del usuario
 * @returns {Promise<{session_id: string, message: string, message_type: string, options: Array|null, diagnosis: Object|null}>}
 */
export async function sendMessage(sessionId, message) {
  return apiFetch('/session/message', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, message }),
  })
}

/**
 * Recupera el estado de una sesión.
 * @param {string} sessionId - UUID de la sesión
 * @returns {Promise<Object>}
 */
export async function getSession(sessionId) {
  return apiFetch(`/session/${sessionId}`)
}

/**
 * Registra el feedback del usuario.
 * @param {string} sessionId - UUID de la sesión
 * @param {boolean} useful - ¿Fue útil?
 * @param {string} [comment] - Comentario opcional
 * @returns {Promise<Object>}
 */
export async function submitFeedback(sessionId, useful, comment = '') {
  return apiFetch(`/session/${sessionId}/feedback`, {
    method: 'POST',
    body: JSON.stringify({ useful, comment: comment || null }),
  })
}

/**
 * Obtiene las métricas del sistema.
 * @returns {Promise<Object>}
 */
export async function getMetrics() {
  return apiFetch('/metrics/summary')
}

/**
 * Comprueba el estado de salud del backend.
 * @returns {Promise<Object>}
 */
export async function checkHealth() {
  return apiFetch('/health')
}

/**
 * Lista sesiones recientes (analítica).
 * @param {number} [limit=20]
 * @returns {Promise<Object>}
 */
export async function getAnalyticsSessions(limit = 20) {
  return apiFetch(`/analytics/sessions?limit=${limit}`)
}

/**
 * Ranking de diagnósticos más frecuentes.
 * @returns {Promise<Object>}
 */
export async function getAnalyticsDiagnoses() {
  return apiFetch('/analytics/diagnoses')
}

/**
 * Lista de feedback recibido.
 * @param {number} [limit=20]
 * @returns {Promise<Object>}
 */
export async function getAnalyticsFeedback(limit = 20) {
  return apiFetch(`/analytics/feedback?limit=${limit}`)
}

/**
 * Lista de FAQs de la base de conocimiento.
 * @param {Object} [filters]
 * @returns {Promise<Object>}
 */
export async function getKnowledgeFaqs(filters = {}) {
  const params = new URLSearchParams(filters).toString()
  return apiFetch(`/knowledge/faqs${params ? '?' + params : ''}`)
}

/**
 * Lista de casos históricos de la base de conocimiento.
 * @param {Object} [filters]
 * @returns {Promise<Object>}
 */
export async function getKnowledgeCases(filters = {}) {
  const params = new URLSearchParams(filters).toString()
  return apiFetch(`/knowledge/cases${params ? '?' + params : ''}`)
}

/**
 * Lista de árboles de diagnóstico disponibles.
 * @returns {Promise<Object>}
 */
export async function getKnowledgeTrees() {
  return apiFetch('/knowledge/trees')
}

/**
 * Mapa de calor de síntomas por modelo.
 * @returns {Promise<{models: string[], symptoms: string[], rows: Object[], max_value: number}>}
 */
export async function getHeatmap() {
  return apiFetch('/analytics/heatmap')
}
