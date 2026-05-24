/**
 * Barra de progreso de fases del flujo de diagnóstico.
 * Fases: VIN → Menú → Diagnóstico → Feedback
 * El prop `phase` es: 'vin' | 'menu' | 'diagnosis' | 'feedback'
 */
const PHASES = [
  { key: 'vin',       label: 'Identificación',  icon: '🔑' },
  { key: 'menu',      label: 'Consulta',         icon: '📋' },
  { key: 'diagnosis', label: 'Diagnóstico',      icon: '🔍' },
  { key: 'feedback',  label: 'Valoración',       icon: '⭐' },
]

export default function PhaseBar({ phase }) {
  const currentIdx = PHASES.findIndex(p => p.key === phase)

  return (
    <div className="bg-gray-900 border-b border-gray-800 px-4 py-2">
      <div className="max-w-3xl mx-auto flex items-center gap-0">
        {PHASES.map((p, idx) => {
          const isDone    = idx < currentIdx
          const isActive  = idx === currentIdx
          const isPending = idx > currentIdx

          return (
            <div key={p.key} className="flex items-center flex-1">
              {/* Step */}
              <div className="flex flex-col items-center gap-0.5 min-w-[64px]">
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold transition-all
                    ${isDone    ? 'bg-green-600 text-white shadow-sm shadow-green-900/50' : ''}
                    ${isActive  ? 'bg-blue-600 text-white shadow-md shadow-blue-900/60 ring-2 ring-blue-500/40' : ''}
                    ${isPending ? 'bg-gray-800 text-gray-600 border border-gray-700' : ''}
                  `}
                >
                  {isDone ? '✓' : p.icon}
                </div>
                <span
                  className={`text-[10px] font-medium leading-tight text-center
                    ${isDone    ? 'text-green-500' : ''}
                    ${isActive  ? 'text-blue-400' : ''}
                    ${isPending ? 'text-gray-600' : ''}
                  `}
                >
                  {p.label}
                </span>
              </div>

              {/* Connector line (no mostrar después del último) */}
              {idx < PHASES.length - 1 && (
                <div
                  className={`flex-1 h-0.5 mx-1 rounded transition-all
                    ${idx < currentIdx ? 'bg-green-700' : 'bg-gray-800'}
                  `}
                />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
