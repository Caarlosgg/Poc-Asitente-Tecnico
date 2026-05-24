import { useState } from 'react'
import { getMetrics, getAnalyticsSessions, getAnalyticsDiagnoses, getAnalyticsFeedback } from '../../services/api'

/**
 * Exportador de informe PDF del sistema.
 * Genera un documento HTML descriptivo y abre el diálogo de impresión del navegador.
 * No requiere bibliotecas externas.
 */

function formatDate(isoString) {
  if (!isoString) return '—'
  const d = new Date(isoString)
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function buildHtml(metrics, sessions, diagnoses, feedback, generatedAt) {
  const totalSessions = metrics?.total_sessions ?? '—'
  const closedSessions = metrics?.closed_sessions ?? '—'
  const avgSteps = metrics?.avg_steps_per_session != null ? metrics.avg_steps_per_session.toFixed(1) : '—'
  const posRate = feedback?.positive_rate != null ? (feedback.positive_rate * 100).toFixed(1) + '%' : '—'

  const diagRows = (diagnoses?.items || [])
    .map(d => `<tr><td>${d.diagnosis || '—'}</td><td>${d.model || '—'}</td><td style="text-align:center">${d.count}</td></tr>`)
    .join('')

  const sessionRows = (sessions?.items || []).slice(0, 20)
    .map(s => `<tr>
      <td style="font-size:9px">${s.session_id?.slice(0, 8)}…</td>
      <td>${s.vin || '—'}</td>
      <td>${s.model || '—'}</td>
      <td>${s.status || '—'}</td>
      <td>${s.total_steps ?? '—'}</td>
      <td>${s.final_result || '—'}</td>
      <td>${formatDate(s.started_at)}</td>
    </tr>`)
    .join('')

  const feedbackRows = (feedback?.items || []).slice(0, 10)
    .map(f => `<tr>
      <td style="font-size:9px">${f.session_id?.slice(0, 8)}…</td>
      <td style="text-align:center">${f.useful ? '✓ Útil' : '✗ No útil'}</td>
      <td>${f.comment || '—'}</td>
      <td>${formatDate(f.created_at)}</td>
    </tr>`)
    .join('')

  return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <title>Informe del Asistente Técnico</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; color: #1a1a2e; line-height: 1.5; padding: 20px 30px; }
    h1 { font-size: 20px; color: #0f3460; border-bottom: 2px solid #0f3460; padding-bottom: 6px; margin-bottom: 4px; }
    .subtitle { color: #555; font-size: 10px; margin-bottom: 20px; }
    h2 { font-size: 13px; color: #16213e; margin: 20px 0 8px; border-left: 3px solid #0f3460; padding-left: 8px; }
    .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 20px; }
    .kpi { background: #f0f4ff; border-radius: 8px; padding: 12px; text-align: center; }
    .kpi-val { font-size: 24px; font-weight: 700; color: #0f3460; }
    .kpi-lbl { font-size: 9px; color: #666; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 16px; font-size: 10px; }
    th { background: #0f3460; color: white; padding: 5px 8px; text-align: left; font-size: 9px; text-transform: uppercase; letter-spacing: 0.04em; }
    td { padding: 4px 8px; border-bottom: 1px solid #eee; color: #333; }
    tr:nth-child(even) td { background: #f7f9ff; }
    .badge-ok { color: #166534; background: #dcfce7; padding: 1px 6px; border-radius: 9999px; font-size: 9px; }
    .badge-fail { color: #991b1b; background: #fee2e2; padding: 1px 6px; border-radius: 9999px; font-size: 9px; }
    footer { margin-top: 30px; border-top: 1px solid #ddd; padding-top: 8px; font-size: 9px; color: #888; text-align: center; }
    @media print {
      body { padding: 10px 15px; }
      .no-print { display: none; }
      h2 { page-break-before: auto; }
    }
  </style>
</head>
<body>
  <h1>📋 Informe del Asistente Técnico</h1>
  <p class="subtitle">Generado el ${generatedAt} · Sistema de Diagnóstico Guiado (POC)</p>

  <h2>Resumen ejecutivo</h2>
  <div class="kpi-grid">
    <div class="kpi"><div class="kpi-val">${totalSessions}</div><div class="kpi-lbl">Sesiones totales</div></div>
    <div class="kpi"><div class="kpi-val">${closedSessions}</div><div class="kpi-lbl">Completadas</div></div>
    <div class="kpi"><div class="kpi-val">${avgSteps}</div><div class="kpi-lbl">Pasos promedio</div></div>
    <div class="kpi"><div class="kpi-val">${posRate}</div><div class="kpi-lbl">Valoración positiva</div></div>
  </div>

  <h2>Diagnósticos más frecuentes</h2>
  <table>
    <thead><tr><th>Diagnóstico</th><th>Modelo</th><th style="text-align:center">Casos</th></tr></thead>
    <tbody>${diagRows || '<tr><td colspan="3" style="text-align:center;color:#999">Sin datos</td></tr>'}</tbody>
  </table>

  <h2>Sesiones recientes (últimas 20)</h2>
  <table>
    <thead>
      <tr>
        <th>ID</th><th>VIN</th><th>Modelo</th><th>Estado</th><th>Pasos</th><th>Diagnóstico final</th><th>Inicio</th>
      </tr>
    </thead>
    <tbody>${sessionRows || '<tr><td colspan="7" style="text-align:center;color:#999">Sin sesiones</td></tr>'}</tbody>
  </table>

  <h2>Feedback reciente (últimas 10 valoraciones)</h2>
  <table>
    <thead><tr><th>Sesión</th><th style="text-align:center">Valoración</th><th>Comentario</th><th>Fecha</th></tr></thead>
    <tbody>${feedbackRows || '<tr><td colspan="4" style="text-align:center;color:#999">Sin feedback</td></tr>'}</tbody>
  </table>

  <footer>
    Asistente Técnico de Diagnóstico Guiado · POC · ${generatedAt}
  </footer>
</body>
</html>`
}

export default function PdfExport() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleExport() {
    setLoading(true)
    setError(null)
    try {
      const [metrics, sessions, diagnoses, feedback] = await Promise.all([
        getMetrics(),
        getAnalyticsSessions(50),
        getAnalyticsDiagnoses(),
        getAnalyticsFeedback(50),
      ])

      const generatedAt = new Date().toLocaleString('es-ES', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit',
      })

      const html = buildHtml(metrics, sessions, diagnoses, feedback, generatedAt)

      // Abrir en ventana nueva y lanzar impresión
      const win = window.open('', '_blank', 'width=900,height=700')
      if (!win) {
        setError('El navegador bloqueó la ventana emergente. Permite popups para este sitio.')
        return
      }
      win.document.write(html)
      win.document.close()
      win.focus()
      setTimeout(() => win.print(), 600)
    } catch (e) {
      setError(e.message || 'Error al generar el informe.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="px-3 py-3 space-y-3">
      {/* Descripción */}
      <div className="bg-gray-800/50 rounded-xl p-3 text-xs text-gray-400 leading-relaxed border border-gray-700/50">
        <p className="font-semibold text-gray-300 mb-1">📄 Informe descriptivo completo</p>
        <p>Genera un documento PDF con:</p>
        <ul className="list-disc list-inside mt-1 space-y-0.5 text-gray-500">
          <li>KPIs del sistema (sesiones, diagnósticos, feedback)</li>
          <li>Ranking de diagnósticos más frecuentes por modelo</li>
          <li>Historial de sesiones recientes</li>
          <li>Valoraciones y comentarios de feedback</li>
        </ul>
      </div>

      {/* Botón */}
      <button
        onClick={handleExport}
        disabled={loading}
        className={`w-full flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-sm transition-all duration-150 border
          ${loading
            ? 'bg-gray-800 text-gray-600 border-gray-700 cursor-wait'
            : 'bg-gradient-to-r from-blue-900/60 to-blue-800/40 hover:from-blue-800/70 hover:to-blue-700/50 text-blue-200 border-blue-700/50 hover:border-blue-500 active:scale-[0.98] shadow-lg hover:shadow-blue-900/40'
          }
        `}
      >
        {loading ? (
          <>
            <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
            Generando informe…
          </>
        ) : (
          <>
            <span className="text-lg">⬇️</span>
            Exportar informe PDF
          </>
        )}
      </button>

      {error && (
        <p className="text-xs text-red-400 bg-red-950/30 border border-red-900/40 rounded-lg px-3 py-2">
          {error}
        </p>
      )}

      <p className="text-[9px] text-gray-700 text-center">
        Se abrirá el diálogo de impresión del navegador · Guardar como PDF
      </p>
    </div>
  )
}
