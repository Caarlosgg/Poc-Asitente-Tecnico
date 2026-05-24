import { useState, useEffect } from 'react'
import { getHeatmap } from '../../services/api'

/**
 * Mapa de calor de síntomas por modelo.
 * Eje X: modelos de vehículo. Eje Y: síntomas.
 * Cada celda se colorea según la frecuencia de diagnósticos.
 */

function cellColor(value, maxValue) {
  if (value === 0 || maxValue === 0) return 'bg-gray-900 text-gray-700'
  const ratio = value / maxValue
  if (ratio >= 0.75) return 'bg-red-600/80 text-white'
  if (ratio >= 0.5)  return 'bg-orange-500/70 text-white'
  if (ratio >= 0.25) return 'bg-yellow-500/60 text-gray-900'
  return 'bg-green-700/50 text-gray-200'
}

function cellIntensity(value, maxValue) {
  if (value === 0 || maxValue === 0) return 0
  return Math.round((value / maxValue) * 100)
}

export default function SymptomHeatMap() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [tooltip, setTooltip] = useState(null) // { x, y, symptom, model, count }

  useEffect(() => {
    getHeatmap()
      .then(setData)
      .catch(e => setError(e.message || 'Error al cargar el mapa de calor.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="px-3 py-6 text-center text-xs text-gray-500">
        Cargando mapa de calor...
      </div>
    )
  }

  if (error) {
    return (
      <div className="px-3 py-4 text-center text-xs text-red-400">{error}</div>
    )
  }

  if (!data || data.models.length === 0) {
    return (
      <div className="px-3 py-4 text-center text-xs text-gray-500">
        No hay datos suficientes aún.
      </div>
    )
  }

  const { models, symptoms, rows, max_value } = data

  // Abreviar nombre de modelos para que quepan en el grid
  const shortModel = (m) => m.length > 12 ? m.slice(0, 11) + '…' : m

  return (
    <div className="px-2 py-3 space-y-3">
      {/* Leyenda */}
      <div className="flex items-center gap-2 px-1">
        <span className="text-[9px] text-gray-600 font-semibold uppercase tracking-wider">Intensidad:</span>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-sm bg-gray-900 border border-gray-800" />
          <span className="text-[9px] text-gray-600">0</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-sm bg-green-700/50" />
          <span className="text-[9px] text-gray-600">bajo</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-sm bg-yellow-500/60" />
          <span className="text-[9px] text-gray-600">medio</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-sm bg-orange-500/70" />
          <span className="text-[9px] text-gray-600">alto</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-sm bg-red-600/80" />
          <span className="text-[9px] text-gray-600">crítico</span>
        </div>
      </div>

      {/* Grid principal */}
      <div className="overflow-x-auto">
        <table className="w-full text-[10px] border-collapse">
          <thead>
            <tr>
              {/* Cabecera: síntoma label */}
              <th className="text-left pb-1 pr-2 text-gray-600 font-medium w-32 min-w-[100px]">
                Síntoma / Modelo
              </th>
              {models.map(m => (
                <th
                  key={m}
                  className="text-center pb-1 px-1 text-gray-400 font-semibold whitespace-nowrap"
                  title={m}
                >
                  {shortModel(m)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, ri) => (
              <tr key={ri} className="group">
                {/* Etiqueta de síntoma */}
                <td className="pr-2 py-0.5 text-gray-400 font-medium leading-tight whitespace-nowrap text-[9px]">
                  {row.symptom}
                </td>
                {/* Celdas de valor */}
                {models.map(model => {
                  const val = row[model] ?? 0
                  const color = cellColor(val, max_value)
                  return (
                    <td
                      key={model}
                      className="px-1 py-0.5 text-center"
                      onMouseEnter={e => setTooltip({ symptom: row.symptom, model, count: val, x: e.clientX, y: e.clientY })}
                      onMouseLeave={() => setTooltip(null)}
                    >
                      <div
                        className={`rounded w-full h-6 flex items-center justify-center font-bold transition-all cursor-default
                          ${color} ${val > 0 ? 'hover:ring-1 hover:ring-white/20 hover:scale-105' : ''}
                        `}
                        title={`${model} · ${row.symptom}: ${val}`}
                      >
                        {val > 0 ? val : ''}
                      </div>
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Tooltip flotante */}
      {tooltip && (
        <div
          className="fixed z-50 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 shadow-xl pointer-events-none text-xs"
          style={{ left: tooltip.x + 12, top: tooltip.y - 40 }}
        >
          <p className="text-gray-200 font-semibold">{tooltip.model}</p>
          <p className="text-gray-400">{tooltip.symptom}</p>
          <p className="text-white font-bold mt-0.5">
            {tooltip.count} {tooltip.count === 1 ? 'caso' : 'casos'}
          </p>
        </div>
      )}

      {/* Máximo */}
      <p className="text-[9px] text-gray-700 text-right px-1">
        Máx. en el período: {max_value} casos
      </p>
    </div>
  )
}
