/**
 * Badge de confianza del diagnóstico.
 * Verde si > 0.8, amarillo si 0.5–0.8, rojo si < 0.5
 */
export default function ConfidenceBadge({ confidence }) {
  const pct = Math.round(confidence * 100)

  const colorClass =
    confidence >= 0.8
      ? 'bg-green-900/50 text-green-300 border-green-600'
      : confidence >= 0.5
      ? 'bg-yellow-900/50 text-yellow-300 border-yellow-600'
      : 'bg-red-900/50 text-red-300 border-red-600'

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-mono font-semibold border ${colorClass}`}
    >
      <span>Confianza:</span>
      <span>{pct}%</span>
    </span>
  )
}
