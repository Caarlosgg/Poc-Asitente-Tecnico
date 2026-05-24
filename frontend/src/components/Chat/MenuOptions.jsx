/**
 * Menú de opciones principales (síntomas/rutas).
 * Diseño visual enriquecido con emojis, gradientes, animaciones y badges de ruta.
 */

const OPTION_META = {
  symptom_motor: {
    icon: '⚡',
    description: 'Motor se apaga o tiene pérdida de potencia',
    route: 'A',
    badge: 'Árbol DDT',
    gradient: 'from-green-950/80 to-green-900/30',
    border: 'border-green-800/50 hover:border-green-600',
    accent: 'text-green-400',
    badgeStyle: 'bg-green-900/60 text-green-300 border-green-700/50',
    glow: 'hover:shadow-green-900/30',
  },
  symptom_arranque: {
    icon: '🔑',
    description: 'Motor no arranca o arranca con dificultad',
    route: 'A',
    badge: 'Árbol DDT',
    gradient: 'from-green-950/80 to-green-900/30',
    border: 'border-green-800/50 hover:border-green-600',
    accent: 'text-green-400',
    badgeStyle: 'bg-green-900/60 text-green-300 border-green-700/50',
    glow: 'hover:shadow-green-900/30',
  },
  symptom_celp: {
    icon: '⚠️',
    description: 'Testigo de avería electrónica encendido',
    route: 'A',
    badge: 'Árbol DDT',
    gradient: 'from-yellow-950/80 to-yellow-900/20',
    border: 'border-yellow-800/50 hover:border-yellow-600',
    accent: 'text-yellow-400',
    badgeStyle: 'bg-yellow-900/60 text-yellow-300 border-yellow-700/50',
    glow: 'hover:shadow-yellow-900/30',
  },
  symptom_consumo: {
    icon: '⛽',
    description: 'Consumo excesivo de combustible o aceite',
    route: 'A',
    badge: 'Árbol DDT',
    gradient: 'from-orange-950/80 to-orange-900/20',
    border: 'border-orange-800/50 hover:border-orange-600',
    accent: 'text-orange-400',
    badgeStyle: 'bg-orange-900/60 text-orange-300 border-orange-700/50',
    glow: 'hover:shadow-orange-900/30',
  },
  faq: {
    icon: '📚',
    description: 'Mantenimiento, procedimientos y preguntas frecuentes',
    route: 'B',
    badge: 'Base FAQ',
    gradient: 'from-blue-950/80 to-blue-900/20',
    border: 'border-blue-800/50 hover:border-blue-600',
    accent: 'text-blue-400',
    badgeStyle: 'bg-blue-900/60 text-blue-300 border-blue-700/50',
    glow: 'hover:shadow-blue-900/30',
    wide: true,
  },
  other: {
    icon: '💬',
    description: 'Describe el problema con tus palabras y el asistente lo analiza',
    route: 'C',
    badge: 'IA Libre',
    gradient: 'from-purple-950/80 to-purple-900/20',
    border: 'border-purple-800/50 hover:border-purple-600',
    accent: 'text-purple-400',
    badgeStyle: 'bg-purple-900/60 text-purple-300 border-purple-700/50',
    glow: 'hover:shadow-purple-900/30',
    wide: true,
  },
}

const ROUTE_LABELS = {
  A: { color: 'text-green-400', label: 'Diagnóstico estructurado' },
  B: { color: 'text-blue-400', label: 'Consulta de conocimiento' },
  C: { color: 'text-purple-400', label: 'Análisis libre por IA' },
}

export default function MenuOptions({ options, onSelect, disabled }) {
  if (!options || options.length === 0) return null

  // Separar opciones normales (síntomas) de las opciones wide (faq, other)
  const mainOptions = options.filter(o => !OPTION_META[o.id]?.wide)
  const wideOptions = options.filter(o => OPTION_META[o.id]?.wide)

  const renderCard = (option) => {
    const meta = OPTION_META[option.id] || {
      icon: '🔧',
      description: '',
      gradient: 'from-gray-900 to-gray-800',
      border: 'border-gray-700 hover:border-gray-500',
      accent: 'text-gray-300',
      badgeStyle: 'bg-gray-800 text-gray-400 border-gray-700',
      glow: 'hover:shadow-gray-900/30',
    }
    const routeInfo = meta.route ? ROUTE_LABELS[meta.route] : null

    return (
      <button
        key={option.id}
        onClick={() => onSelect(option.id, option.label)}
        disabled={disabled}
        className={`group relative text-left rounded-xl border transition-all duration-200
          bg-gradient-to-br ${meta.gradient} ${meta.border}
          hover:shadow-lg ${meta.glow}
          ${disabled
            ? 'opacity-40 cursor-not-allowed'
            : 'cursor-pointer hover:-translate-y-0.5 active:translate-y-0 active:scale-[0.99]'
          }
          p-4
        `}
      >
        {/* Icono grande + badge de ruta */}
        <div className="flex items-start justify-between mb-3">
          <span className="text-3xl leading-none group-hover:scale-110 transition-transform duration-200 inline-block">
            {meta.icon}
          </span>
          {meta.badge && (
            <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full border ${meta.badgeStyle}`}>
              {meta.badge}
            </span>
          )}
        </div>

        {/* Etiqueta */}
        <p className={`text-sm font-semibold mb-1 ${meta.accent}`}>{option.label}</p>

        {/* Descripción */}
        {meta.description && (
          <p className="text-[11px] text-gray-500 leading-snug">{meta.description}</p>
        )}

        {/* Indicador de ruta inferior */}
        {routeInfo && (
          <div className={`mt-3 pt-2 border-t border-white/5 text-[9px] font-medium ${routeInfo.color} opacity-70`}>
            Ruta {meta.route} · {routeInfo.label}
          </div>
        )}

        {/* Brillo al hover */}
        <div className="absolute inset-0 rounded-xl bg-white/[0.02] opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
      </button>
    )
  }

  return (
    <div className="px-3 py-3 space-y-2">
      {/* Síntomas en grid 2 columnas */}
      {mainOptions.length > 0 && (
        <div className="grid grid-cols-2 gap-2">
          {mainOptions.map(renderCard)}
        </div>
      )}
      {/* FAQ y libre en ancho completo */}
      {wideOptions.length > 0 && (
        <div className="grid grid-cols-1 gap-2">
          {wideOptions.map(option => {
            const meta = OPTION_META[option.id] || {}
            const routeInfo = meta.route ? ROUTE_LABELS[meta.route] : null
            return (
              <button
                key={option.id}
                onClick={() => onSelect(option.id, option.label)}
                disabled={disabled}
                className={`group relative text-left rounded-xl border transition-all duration-200
                  bg-gradient-to-br ${meta.gradient} ${meta.border}
                  hover:shadow-lg ${meta.glow}
                  ${disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer hover:-translate-y-0.5 active:translate-y-0 active:scale-[0.99]'}
                  px-4 py-3 flex items-center gap-4
                `}
              >
                <span className="text-2xl leading-none group-hover:scale-110 transition-transform duration-200 inline-block shrink-0">
                  {meta.icon}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <p className={`text-sm font-semibold ${meta.accent}`}>{option.label}</p>
                    {meta.badge && (
                      <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full border ${meta.badgeStyle}`}>
                        {meta.badge}
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-gray-500 leading-snug">{meta.description}</p>
                </div>
                {routeInfo && (
                  <span className={`text-[9px] font-medium ${routeInfo.color} opacity-60 shrink-0`}>
                    Ruta {meta.route}
                  </span>
                )}
                <div className="absolute inset-0 rounded-xl bg-white/[0.02] opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}

