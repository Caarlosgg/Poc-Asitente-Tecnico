import { useState, useEffect } from 'react'
import { getSession } from '../../services/api'

/**
 * F1: Panel de resumen de sesión.
 * Muestra información completa de la sesión tras finalizar el diagnóstico.
 * Se activa con el botón "Ver resumen" en la pantalla post-diagnóstico.
 */
export default function SessionSummaryPanel({ sessionId, onClose }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!sessionId) return
    setLoading(true)
    getSession(sessionId)
      .then(setData)
      .catch(e => setError(e.message || 'Error al cargar el resumen.'))
      .finally(() => setLoading(false))
  }, [sessionId])

  const ROUTE_LABELS = {
    tree:  { label: 'Árbol de diagnóstico', icon: '🌳', color: 'text-green-400' },
    faq:   { label: 'Base de FAQs',         icon: '📚', color: 'text-blue-400' },
    other: { label: 'Historial de casos',   icon: '📂', color: 'text-purple-400' },
  }

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-800">
          <div className="flex items-center gap-2">
            <span className="text-lg">📋</span>
            <span className="text-sm font-bold text-gray-100">Resumen de sesión</span>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-300 text-xl leading-none transition-colors"
          >
            ×
          </button>
        </div>

        {/* Contenido */}
        <div className="px-5 py-4 space-y-4 overflow-y-auto max-h-[70vh]">
          {loading && (
            <p className="text-gray-500 text-sm text-center py-4">Cargando resumen...</p>
          )}

          {error && (
            <p className="text-red-400 text-sm text-center py-4">{error}</p>
          )}

          {data && !loading && (
            <>
              {/* Vehículo */}
              <section>
                <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2">Vehículo</h3>
                <div className="bg-gray-800 rounded-xl p-3 grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-500">Bastidor</span>
                    <p className="text-gray-200 font-mono mt-0.5">{data.vin || '—'}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Modelo</span>
                    <p className="text-green-300 font-semibold mt-0.5">{data.model || '—'}</p>
                  </div>
                </div>
              </section>

              {/* Estadísticas de la sesión */}
              <section>
                <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2">Estadísticas</h3>
                <div className="bg-gray-800 rounded-xl p-3 grid grid-cols-3 gap-3 text-xs text-center">
                  <div>
                    <p className="text-2xl font-bold text-blue-400">{data.total_steps ?? '—'}</p>
                    <p className="text-gray-500 mt-0.5">Pasos</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-gray-200">{data.messages?.length ?? '—'}</p>
                    <p className="text-gray-500 mt-0.5">Mensajes</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-green-400">
                      {data.status === 'closed' ? '✓' : '…'}
                    </p>
                    <p className="text-gray-500 mt-0.5">Estado</p>
                  </div>
                </div>
              </section>

              {/* Ruta utilizada */}
              {data.entry_point && (
                <section>
                  <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2">Ruta de diagnóstico</h3>
                  <div className="bg-gray-800 rounded-xl p-3 text-xs">
                    {(() => {
                      const routeKey = data.entry_point?.includes('faq') ? 'faq'
                        : data.entry_point?.includes('tree') || data.entry_point?.includes('symptom') ? 'tree'
                        : 'other'
                      const cfg = ROUTE_LABELS[routeKey] || ROUTE_LABELS.other
                      return (
                        <span className={`flex items-center gap-2 font-semibold ${cfg.color}`}>
                          <span>{cfg.icon}</span>
                          {cfg.label}
                        </span>
                      )
                    })()}
                  </div>
                </section>
              )}

              {/* Diagnóstico final */}
              {data.final_result && (
                <section>
                  <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2">Diagnóstico final</h3>
                  <div className="bg-green-950/30 border border-green-800/40 rounded-xl p-3 text-sm text-green-300 font-semibold">
                    {data.final_result}
                  </div>
                </section>
              )}

              {/* Historial de mensajes */}
              {data.messages && data.messages.length > 0 && (
                <section>
                  <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2">
                    Conversación ({data.messages.length} mensajes)
                  </h3>
                  <div className="space-y-1 max-h-48 overflow-y-auto pr-1">
                    {data.messages.map((msg, i) => (
                      <div
                        key={i}
                        className={`text-xs px-3 py-1.5 rounded-lg ${
                          msg.role === 'user'
                            ? 'bg-blue-900/30 text-blue-200 ml-8'
                            : 'bg-gray-800 text-gray-300'
                        }`}
                      >
                        <span className="text-[9px] text-gray-600 font-bold uppercase mr-1">
                          {msg.role === 'user' ? 'Técnico' : 'Asistente'}:
                        </span>
                        {msg.content}
                      </div>
                    ))}
                  </div>
                </section>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-gray-800">
          <button
            onClick={onClose}
            className="w-full py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm transition-colors"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  )
}
