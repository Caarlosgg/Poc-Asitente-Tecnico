import { useState, useCallback } from 'react'
import { sendMessage } from '../services/api'
import { ROLES } from '../utils/messageTypes'

/**
 * Hook para gestionar el historial de mensajes y el envío al backend.
 *
 * @param {string|null} sessionId - UUID de la sesión activa
 * @returns {{ messages: Array, loading: boolean, error: string|null, send: Function, addMessage: Function }}
 */
export function useChat(sessionId) {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  /**
   * Añade un mensaje al historial local sin llamar al backend.
   * Útil para mensajes de sistema o bienvenida.
   */
  const addMessage = useCallback((role, content, messageType = 'text', options = null, diagnosis = null, route = null) => {
    setMessages(prev => [
      ...prev,
      {
        id: Date.now() + Math.random(),
        role,
        content,
        messageType,
        options,
        diagnosis,
        route,
        stepNumber: null,
        suggestsTree: null,
        timestamp: new Date().toISOString(),
      },
    ])
  }, [])

  /**
   * Envía un mensaje del usuario al backend y añade la respuesta al historial.
   *
   * @param {string} message - Texto del usuario o ID de opción seleccionada
   * @param {string} [displayText] - Texto visible al usuario (si difiere del valor enviado)
   */
  const send = useCallback(async (message, displayText = null) => {
    if (!sessionId || !message.trim() || loading) return

    const userText = displayText || message

    // Añadir mensaje del usuario al historial
    setMessages(prev => [
      ...prev,
      {
        id: Date.now(),
        role: ROLES.USER,
        content: userText,
        messageType: 'text',
        options: null,
        diagnosis: null,
        timestamp: new Date().toISOString(),
      },
    ])

    setLoading(true)
    setError(null)

    try {
      const response = await sendMessage(sessionId, message)

      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          role: ROLES.ASSISTANT,
          content: response.message,
          messageType: response.message_type,
          options: response.options || null,
          diagnosis: response.diagnosis || null,
          route: response.route || null,
          stepNumber: response.step_number || null,
          suggestsTree: response.suggests_tree || null,
          timestamp: new Date().toISOString(),
        },
      ])

      return response
    } catch (err) {
      const errorMsg = err.message || 'Error al comunicarse con el servidor.'
      setError(errorMsg)
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 2,
          role: ROLES.ASSISTANT,
          content: `Error: ${errorMsg}`,
          messageType: 'error',
          options: null,
          diagnosis: null,
          timestamp: new Date().toISOString(),
        },
      ])
      return null
    } finally {
      setLoading(false)
    }
  }, [sessionId, loading])

  const clearError = useCallback(() => setError(null), [])

  return { messages, loading, error, send, addMessage, clearError }
}
