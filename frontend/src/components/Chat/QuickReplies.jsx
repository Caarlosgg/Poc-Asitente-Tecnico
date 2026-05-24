/**
 * Botones de respuesta rápida (Sí / No / opciones) para preguntas del árbol de diagnóstico.
 */
export default function QuickReplies({ options, onSelect, disabled }) {
  if (!options || options.length === 0) return null

  const isPrimary = (id) =>
    id === 'si' || id === 'menu' || id === 'continue' || id === 'finish'

  return (
    <div className="flex flex-wrap gap-2 px-4 py-2">
      {options.map(option => (
        <button
          key={option.id}
          onClick={() => onSelect(option.id, option.label)}
          disabled={disabled}
          className={`px-5 py-2 rounded-full text-sm font-medium transition-all duration-150
            border shadow-sm active:scale-95
            ${
              disabled
                ? 'opacity-40 cursor-not-allowed bg-gray-800 text-gray-500 border-gray-700'
                : isPrimary(option.id)
                ? 'bg-blue-600 hover:bg-blue-500 text-white border-blue-500/50 shadow-blue-900/30'
                : 'bg-gray-800 hover:bg-gray-700 text-gray-200 border-gray-700/60 hover:border-gray-600'
            }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  )
}
