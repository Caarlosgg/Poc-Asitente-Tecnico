/**
 * Cabecera de sección inline en el chat.
 * Aparece cuando el flujo entra en una Ruta A, B o C.
 * route: 'tree' | 'faq' | 'other'
 * symptom: nombre del síntoma (opcional, para Ruta A)
 */
const ROUTE_CONFIG = {
  tree: {
    label: 'Ruta A — Árbol de Diagnóstico',
    icon: '🌳',
    color: 'border-green-700/50 text-green-400 bg-green-950/30',
    lineColor: 'bg-green-800/40',
  },
  faq: {
    label: 'Ruta B — Base de Conocimiento',
    icon: '📚',
    color: 'border-blue-700/50 text-blue-400 bg-blue-950/30',
    lineColor: 'bg-blue-800/40',
  },
  other: {
    label: 'Ruta C — Historial Híbrido',
    icon: '🔍',
    color: 'border-purple-700/50 text-purple-400 bg-purple-950/30',
    lineColor: 'bg-purple-800/40',
  },
}

export default function RouteHeader({ route, symptom }) {
  const cfg = ROUTE_CONFIG[route]
  if (!cfg) return null

  return (
    <div className="flex items-center gap-3 px-3 py-2 my-2">
      {/* Línea izquierda */}
      <div className={`flex-1 h-px ${cfg.lineColor}`} />

      {/* Badge */}
      <div
        className={`flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs font-semibold ${cfg.color}`}
      >
        <span>{cfg.icon}</span>
        <span>{symptom ? `${symptom}` : cfg.label}</span>
      </div>

      {/* Línea derecha */}
      <div className={`flex-1 h-px ${cfg.lineColor}`} />
    </div>
  )
}
