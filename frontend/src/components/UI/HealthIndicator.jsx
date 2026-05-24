import { useState, useEffect } from 'react'
import { checkHealth } from '../../services/api'

/**
 * Indicador visual de salud del backend en el header (F5).
 * Pulsa cada 30 segundos. Verde/Amarillo/Rojo.
 */
export default function HealthIndicator() {
  const [status, setStatus] = useState('loading') // 'ok' | 'degraded' | 'error' | 'loading'

  async function ping() {
    try {
      const data = await checkHealth()
      setStatus(data?.status === 'ok' ? 'ok' : 'degraded')
    } catch {
      setStatus('error')
    }
  }

  useEffect(() => {
    ping()
    const interval = setInterval(ping, 30000)
    return () => clearInterval(interval)
  }, [])

  const cfg = {
    ok:       { dot: 'bg-green-400 animate-pulse', text: 'Sistema activo',    color: 'text-gray-500' },
    degraded: { dot: 'bg-yellow-400 animate-pulse', text: 'Sistema degradado', color: 'text-yellow-600' },
    error:    { dot: 'bg-red-500',                  text: 'Sin conexión',      color: 'text-red-500' },
    loading:  { dot: 'bg-gray-500 animate-pulse',   text: 'Conectando...',     color: 'text-gray-600' },
  }[status]

  return (
    <div className="flex items-center gap-1.5">
      <span className={`w-2 h-2 rounded-full ${cfg.dot}`} />
      <span className={`text-xs ${cfg.color}`}>{cfg.text}</span>
    </div>
  )
}
