import ConfidenceBadge from './ConfidenceBadge'
import HypothesisList from './HypothesisList'

/** Barra de progreso de confianza */
function ConfidenceBar({ confidence }) {
  const pct = Math.round(confidence * 100)
  const barColor =
    confidence >= 0.8
      ? 'bg-green-500'
      : confidence >= 0.5
      ? 'bg-yellow-500'
      : 'bg-red-500'

  return (
    <div className="mt-2">
      <div className="flex justify-between text-xs text-gray-400 mb-1">
        <span>Nivel de confianza</span>
        <span className="font-mono font-semibold">{pct}%</span>
      </div>
      <div className="w-full h-1.5 bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${barColor}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

/** Mapa de source_type a etiqueta visual */
const SOURCE_LABELS = {
  tree: { label: 'Árbol de diagnóstico', icon: '🌳' },
  faq: { label: 'Base de conocimiento', icon: '📋' },
  historical: { label: 'Casos históricos', icon: '📂' },
}

/**
 * Tarjeta de resultado de diagnóstico.
 * Muestra hipótesis principal, barra de confianza, alternativas, próxima comprobación y fuente.
 */
export default function DiagnosisResult({ diagnosis, message }) {
  if (!diagnosis) return null

  const source = SOURCE_LABELS[diagnosis.source_type] || { label: diagnosis.source_type, icon: '🔍' }

  return (
    <div className="bg-gray-900/90 border border-green-700/40 rounded-2xl rounded-tl-sm p-4 max-w-full shadow-xl shadow-black/30 ring-1 ring-green-900/20">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-green-500/20 border border-green-600/40 flex items-center justify-center">
            <span className="text-green-400 text-sm">✓</span>
          </div>
          <span className="text-xs font-bold text-green-400 uppercase tracking-widest">
            Diagnóstico completo
          </span>
        </div>
        <ConfidenceBadge confidence={diagnosis.confidence} />
      </div>

      {/* Mensaje intro */}
      {message && (
        <p className="text-gray-300 text-sm mb-3 leading-relaxed border-b border-gray-800 pb-3">{message}</p>
      )}

      {/* Hipótesis principal */}
      <div className="bg-gradient-to-br from-gray-800 to-gray-800/50 border border-green-800/30 rounded-xl p-3 mb-3">
        <p className="text-[10px] text-gray-600 uppercase tracking-widest mb-1.5 flex items-center gap-1">
          <span>🔎</span> Causa probable principal
        </p>
        <p className="text-green-300 font-bold text-base leading-snug">{diagnosis.primary_hypothesis}</p>
        <ConfidenceBar confidence={diagnosis.confidence} />
      </div>

      {/* Hipótesis alternativas */}
      <HypothesisList alternatives={diagnosis.alternatives} />

      {/* Siguiente comprobación */}
      {diagnosis.next_check && (
        <div className="mt-3 bg-amber-950/30 border border-amber-800/30 rounded-xl p-3">
          <p className="text-[10px] text-amber-600/80 uppercase tracking-widest mb-1.5 flex items-center gap-1">
            <span>🔧</span> Siguiente comprobación recomendada
          </p>
          <p className="text-amber-300 text-sm font-semibold leading-snug">{diagnosis.next_check}</p>
        </div>
      )}

      {/* Explicación */}
      {diagnosis.short_explanation && (
        <div className="mt-3 pt-3 border-t border-gray-800/80">
          <p className="text-[10px] text-gray-600 uppercase tracking-widest mb-1">Razonamiento</p>
          <p className="text-gray-400 text-xs leading-relaxed">{diagnosis.short_explanation}</p>
        </div>
      )}

      {/* Fuente */}
      <div className="mt-3 flex items-center justify-end gap-1.5 border-t border-gray-800/60 pt-2">
        <span className="text-xs opacity-60">{source.icon}</span>
        <span className="text-[10px] text-gray-600">{source.label}</span>
      </div>
    </div>
  )
}
