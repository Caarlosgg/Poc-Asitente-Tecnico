import { useState } from 'react'
import { submitFeedback } from '../../services/api'

/**
 * Modal para recoger el feedback del usuario al finalizar la sesión.
 */
export default function FeedbackModal({ sessionId, onClose }) {
  const [useful, setUseful] = useState(null)
  const [comment, setComment] = useState('')
  const [loading, setLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit() {
    if (useful === null) return
    setLoading(true)
    setError(null)
    try {
      await submitFeedback(sessionId, useful, comment)
      setSubmitted(true)
      setTimeout(onClose, 2000)
    } catch (err) {
      setError(err.message || 'Error al enviar feedback.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 border border-gray-600 rounded-xl p-6 w-full max-w-md shadow-2xl">
        {submitted ? (
          <div className="text-center py-4">
            <p className="text-green-400 text-lg font-semibold">¡Gracias por tu valoración!</p>
            <p className="text-gray-400 text-sm mt-1">Cerrando...</p>
          </div>
        ) : (
          <>
            <h2 className="text-lg font-semibold text-gray-100 mb-4">
              ¿Te fue útil el diagnóstico?
            </h2>

            <div className="flex gap-3 mb-4">
              <button
                onClick={() => setUseful(true)}
                className={`flex-1 py-2 rounded-lg font-medium transition-colors ${
                  useful === true
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                👍 Sí, fue útil
              </button>
              <button
                onClick={() => setUseful(false)}
                className={`flex-1 py-2 rounded-lg font-medium transition-colors ${
                  useful === false
                    ? 'bg-red-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                👎 No fue útil
              </button>
            </div>

            <textarea
              className="w-full bg-gray-700 text-gray-200 rounded-lg p-3 text-sm resize-none border border-gray-600 focus:outline-none focus:border-blue-500"
              rows={3}
              placeholder="Comentario opcional (qué mejorarías, qué funcionó...)"
              value={comment}
              onChange={e => setComment(e.target.value)}
              maxLength={1000}
            />

            {error && <p className="text-red-400 text-xs mt-2">{error}</p>}

            <div className="flex gap-3 mt-4">
              <button
                onClick={onClose}
                className="flex-1 py-2 rounded-lg text-gray-400 hover:text-gray-200 bg-gray-700 hover:bg-gray-600 transition-colors text-sm"
              >
                Omitir
              </button>
              <button
                onClick={handleSubmit}
                disabled={useful === null || loading}
                className="flex-1 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium transition-colors text-sm"
              >
                {loading ? 'Enviando...' : 'Enviar valoración'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
