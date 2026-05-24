/**
 * Lista de hipótesis alternativas del diagnóstico.
 */
export default function HypothesisList({ alternatives }) {
  if (!alternatives || alternatives.length === 0) return null

  return (
    <div className="mt-3">
      <p className="text-xs text-gray-500 mb-2 font-semibold uppercase tracking-wider flex items-center gap-1">
        <span>⚡</span> Otras posibles causas
      </p>
      <div className="flex flex-col gap-1.5">
        {alternatives.map((alt, i) => (
          <div
            key={i}
            className="flex items-center gap-2 px-3 py-1.5 bg-gray-800/60 text-gray-400 rounded-lg text-xs border border-gray-700/50"
          >
            <span className="text-gray-600 font-mono font-bold shrink-0">{i + 1}.</span>
            <span>{alt}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
