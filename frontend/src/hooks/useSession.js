import { useState, useEffect } from 'react'
import { startSession } from '../services/api'

const SESSION_KEY = 'poc_asistente_session_id'

/**
 * Hook para gestionar el session_id en localStorage.
 * Crea una nueva sesión si no hay ninguna guardada.
 *
 * @returns {{ sessionId: string|null, loading: boolean, error: string|null, resetSession: Function }}
 */
export function useSession() {
  const [sessionId, setSessionId] = useState(() => localStorage.getItem(SESSION_KEY))
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!sessionId) {
      createNewSession()
    }
  }, [])

  async function createNewSession() {
    setLoading(true)
    setError(null)
    try {
      const data = await startSession()
      const sid = data.session_id
      localStorage.setItem(SESSION_KEY, sid)
      setSessionId(sid)
      return { sessionId: sid, welcomeMessage: data }
    } catch (err) {
      setError('No se pudo conectar con el servidor. Verifica que el backend esté activo.')
      return null
    } finally {
      setLoading(false)
    }
  }

  function resetSession() {
    localStorage.removeItem(SESSION_KEY)
    setSessionId(null)
    setError(null)
  }

  return { sessionId, loading, error, createNewSession, resetSession }
}
