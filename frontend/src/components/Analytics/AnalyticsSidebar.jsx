import { useState, useEffect, useCallback } from 'react'
import {
  getMetrics,
  getAnalyticsSessions,
  getAnalyticsDiagnoses,
  getAnalyticsFeedback,
  getKnowledgeFaqs,
  getKnowledgeCases,
  getKnowledgeTrees,
} from '../../services/api'

/**
 * F2: Sidebar de analítica interna.
 * Panel lateral deslizable con métricas, sesiones, diagnósticos, feedback y base de conocimiento.
 */
export default function AnalyticsSidebar({ onClose }) {
  const [tab, setTab] = useState('metrics')

  const TABS = [
    { id: 'metrics',   label: '📊 Métricas',    title: 'Resumen del sistema' },
    { id: 'sessions',  label: '🗂️ Sesiones',    title: 'Sesiones recientes' },
    { id: 'diagnoses', label: '🔎 Diagnósticos', title: 'Diagnósticos frecuentes' },
    { id: 'feedback',  label: '💬 Feedback',     title: 'Valoraciones' },
    { id: 'knowledge', label: '📚 Conocimiento', title: 'Base de conocimiento' },
  ]

  return (
    <aside className="w-80 shrink-0 bg-gray-900 border-l border-gray-800 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800 shrink-0">
        <span className="text-sm font-bold text-gray-200">Panel analítica</span>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-300 text-xl leading-none transition-colors"
          title="Cerrar"
        >
          ×
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-800 shrink-0 overflow-x-auto">
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`shrink-0 px-2.5 py-2 text-[10px] font-medium whitespace-nowrap transition-colors border-b-2 ${
              tab === t.id
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-300'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Contenido de la tab activa */}
      <div className="flex-1 overflow-y-auto">
        {tab === 'metrics'   && <MetricsTab />}
        {tab === 'sessions'  && <SessionsTab />}
        {tab === 'diagnoses' && <DiagnosesTab />}
        {tab === 'feedback'  && <FeedbackTab />}
        {tab === 'knowledge' && <KnowledgeTab />}
      </div>
    </aside>
  )
}

// ── Helpers ─────────────────────────────────────────────────────────────────

function useApiData(fetcher) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = useCallback(() => {
    setLoading(true)
    setError(null)
    fetcher()
      .then(setData)
      .catch(e => setError(e.message || 'Error al cargar datos.'))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { load() }, [load])

  return { data, loading, error, reload: load }
}

function SectionTitle({ children }) {
  return (
    <h3 className="text-[9px] font-bold text-gray-600 uppercase tracking-widest px-4 pt-4 pb-1">
      {children}
    </h3>
  )
}

function StatCard({ label, value, color = 'text-gray-200' }) {
  return (
    <div className="bg-gray-800 rounded-xl p-3 text-center">
      <p className={`text-xl font-bold ${color}`}>{value ?? '—'}</p>
      <p className="text-[10px] text-gray-500 mt-0.5">{label}</p>
    </div>
  )
}

function LoadingState() {
  return <p className="text-gray-600 text-xs text-center py-8">Cargando...</p>
}

function ErrorState({ message, onRetry }) {
  return (
    <div className="text-center py-8">
      <p className="text-red-400 text-xs mb-2">{message}</p>
      <button onClick={onRetry} className="text-xs text-blue-400 hover:text-blue-300">
        Reintentar
      </button>
    </div>
  )
}

// ── Tab: Métricas ────────────────────────────────────────────────────────────

function MetricsTab() {
  const { data, loading, error, reload } = useApiData(getMetrics)

  if (loading) return <LoadingState />
  if (error) return <ErrorState message={error} onRetry={reload} />

  return (
    <div className="pb-4">
      <SectionTitle>Sesiones</SectionTitle>
      <div className="grid grid-cols-2 gap-2 px-4">
        <StatCard label="Total" value={data.total_sessions} color="text-blue-400" />
        <StatCard label="Completadas" value={data.completed_sessions} color="text-green-400" />
        <StatCard label="Pasos promedio" value={data.avg_steps} color="text-yellow-400" />
        <StatCard label="Tasa de éxito" value={data.success_rate ? `${Math.round(data.success_rate * 100)}%` : '—'} color="text-green-400" />
      </div>

      <SectionTitle>Uso por módulo</SectionTitle>
      <div className="grid grid-cols-3 gap-2 px-4">
        <StatCard label="🌳 Árbol" value={data.module_usage?.tree ?? 0} color="text-green-400" />
        <StatCard label="📋 FAQ" value={data.module_usage?.faq ?? 0} color="text-blue-400" />
        <StatCard label="📂 Historial" value={data.module_usage?.free_text ?? 0} color="text-purple-400" />
      </div>

      <SectionTitle>Feedback</SectionTitle>
      <div className="grid grid-cols-2 gap-2 px-4">
        <StatCard label="👍 Positivo" value={data.positive_feedback} color="text-green-400" />
        <StatCard label="👎 Negativo" value={data.negative_feedback} color="text-red-400" />
      </div>

      {data.top_diagnoses?.length > 0 && (
        <>
          <SectionTitle>Top diagnósticos</SectionTitle>
          <ul className="px-4 space-y-1.5">
            {data.top_diagnoses.map((d, i) => (
              <li key={i} className="bg-gray-800 rounded-lg px-3 py-2 text-xs text-gray-300 flex justify-between items-center gap-2">
                <span className="truncate">{d.diagnosis}</span>
                <span className="text-[10px] font-mono text-green-400 shrink-0">{d.count}×</span>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  )
}

// ── Tab: Sesiones ────────────────────────────────────────────────────────────

function SessionsTab() {
  const { data, loading, error, reload } = useApiData(() => getAnalyticsSessions(20))

  if (loading) return <LoadingState />
  if (error) return <ErrorState message={error} onRetry={reload} />

  return (
    <div className="pb-4">
      <SectionTitle>Últimas {data.items?.length} sesiones</SectionTitle>
      <ul className="px-4 space-y-2">
        {(data.items || []).map(s => (
          <li key={s.session_id} className="bg-gray-800 rounded-xl p-3 text-xs space-y-1">
            <div className="flex justify-between items-center">
              <span className="text-green-300 font-semibold">{s.model || '—'}</span>
              <span className={`text-[9px] px-1.5 py-0.5 rounded-full ${
                s.status === 'closed'
                  ? 'bg-green-900/50 text-green-400'
                  : 'bg-yellow-900/50 text-yellow-400'
              }`}>{s.status}</span>
            </div>
            <div className="text-gray-500 font-mono text-[9px]">{s.session_id.slice(0, 18)}…</div>
            {s.final_result && (
              <div className="text-gray-300 truncate">{s.final_result}</div>
            )}
            <div className="flex gap-3 text-gray-600">
              <span>{s.total_steps} pasos</span>
              {s.duration_seconds != null && (
                <span>{s.duration_seconds}s</span>
              )}
            </div>
          </li>
        ))}
        {(!data.items || data.items.length === 0) && (
          <p className="text-gray-600 text-center py-4">No hay sesiones aún.</p>
        )}
      </ul>
    </div>
  )
}

// ── Tab: Diagnósticos ────────────────────────────────────────────────────────

function DiagnosesTab() {
  const { data, loading, error, reload } = useApiData(getAnalyticsDiagnoses)

  if (loading) return <LoadingState />
  if (error) return <ErrorState message={error} onRetry={reload} />

  const maxCount = Math.max(...(data.items || []).map(d => d.count), 1)

  return (
    <div className="pb-4">
      <SectionTitle>Diagnósticos más frecuentes</SectionTitle>
      <ul className="px-4 space-y-2">
        {(data.items || []).map((d, i) => (
          <li key={i} className="bg-gray-800 rounded-xl p-3 text-xs">
            <div className="flex justify-between items-center mb-1.5">
              <span className="text-gray-300 truncate pr-2">{d.diagnosis}</span>
              <span className="text-green-400 font-mono shrink-0">{d.count}×</span>
            </div>
            <div className="w-full h-1 bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-green-600 rounded-full"
                style={{ width: `${Math.round((d.count / maxCount) * 100)}%` }}
              />
            </div>
            {d.model && <p className="text-gray-600 mt-1 text-[9px]">{d.model}</p>}
          </li>
        ))}
        {(!data.items || data.items.length === 0) && (
          <p className="text-gray-600 text-center py-4">Sin datos de diagnóstico aún.</p>
        )}
      </ul>
    </div>
  )
}

// ── Tab: Feedback ────────────────────────────────────────────────────────────

function FeedbackTab() {
  const { data, loading, error, reload } = useApiData(() => getAnalyticsFeedback(20))

  if (loading) return <LoadingState />
  if (error) return <ErrorState message={error} onRetry={reload} />

  return (
    <div className="pb-4">
      {data.total > 0 && (
        <>
          <SectionTitle>Resumen</SectionTitle>
          <div className="grid grid-cols-3 gap-2 px-4">
            <StatCard label="Total" value={data.total} />
            <StatCard label="👍" value={data.positive} color="text-green-400" />
            <StatCard label="👎" value={data.negative} color="text-red-400" />
          </div>
          <div className="px-4 mt-2">
            <div className="bg-gray-800 rounded-xl p-3 text-center">
              <p className="text-lg font-bold text-green-400">
                {Math.round((data.positive_rate || 0) * 100)}%
              </p>
              <p className="text-[10px] text-gray-500">Tasa de valoraciones positivas</p>
            </div>
          </div>
        </>
      )}

      <SectionTitle>Valoraciones recientes</SectionTitle>
      <ul className="px-4 space-y-2">
        {(data.items || []).map((f, i) => (
          <li key={i} className="bg-gray-800 rounded-xl p-3 text-xs space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-lg">{f.useful ? '👍' : '👎'}</span>
              <span className={f.useful ? 'text-green-400' : 'text-red-400'}>
                {f.useful ? 'Útil' : 'No útil'}
              </span>
            </div>
            {f.comment && (
              <p className="text-gray-400 italic">"{f.comment}"</p>
            )}
            <p className="text-gray-600 font-mono text-[9px]">{f.session_id.slice(0, 18)}…</p>
          </li>
        ))}
        {(!data.items || data.items.length === 0) && (
          <p className="text-gray-600 text-center py-4">Sin feedback recibido aún.</p>
        )}
      </ul>
    </div>
  )
}

// ── Tab: Base de conocimiento ────────────────────────────────────────────────

function KnowledgeTab() {
  const [subtab, setSubtab] = useState('faqs')
  const { data: treesData, loading: treesLoading } = useApiData(getKnowledgeTrees)
  const { data: faqsData, loading: faqsLoading, error: faqsError, reload: reloadFaqs } = useApiData(getKnowledgeFaqs)
  const { data: casesData, loading: casesLoading, error: casesError, reload: reloadCases } = useApiData(getKnowledgeCases)

  return (
    <div className="pb-4">
      {/* Resumen de árboles */}
      {!treesLoading && treesData && (
        <>
          <SectionTitle>Árboles disponibles</SectionTitle>
          <ul className="px-4 space-y-1.5">
            {treesData.items.map(t => (
              <li key={t.tree_id} className="bg-gray-800 rounded-lg px-3 py-2 text-xs flex justify-between">
                <span className="text-green-300">{t.tree_id}</span>
                <span className="text-gray-500">{t.node_count} nodos</span>
              </li>
            ))}
          </ul>
        </>
      )}

      {/* Subtabs FAQs / Casos */}
      <div className="flex gap-3 px-4 mt-4 mb-2">
        {['faqs', 'cases'].map(st => (
          <button
            key={st}
            onClick={() => setSubtab(st)}
            className={`text-[10px] font-semibold px-3 py-1 rounded-full transition-colors ${
              subtab === st
                ? 'bg-blue-800 text-blue-200'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            {st === 'faqs' ? `📋 FAQs (${faqsData?.total ?? '…'})` : `📂 Casos (${casesData?.total ?? '…'})`}
          </button>
        ))}
      </div>

      {subtab === 'faqs' && (
        faqsLoading ? <LoadingState /> :
        faqsError ? <ErrorState message={faqsError} onRetry={reloadFaqs} /> : (
          <ul className="px-4 space-y-2">
            {(faqsData?.items || []).slice(0, 20).map(f => (
              <li key={f.faq_id} className="bg-gray-800 rounded-xl p-3 text-xs space-y-1">
                <div className="flex justify-between items-start gap-2">
                  <span className="text-gray-300 font-semibold leading-snug">{f.question}</span>
                  <span className="text-[9px] text-blue-400 shrink-0">{f.usage_count}×</span>
                </div>
                <p className="text-gray-500 line-clamp-2">{f.answer}</p>
                <span className="inline-block text-[9px] bg-gray-700 rounded px-1.5 py-0.5 text-gray-400">
                  {f.category || 'General'} · {f.model || 'Todos'}
                </span>
              </li>
            ))}
          </ul>
        )
      )}

      {subtab === 'cases' && (
        casesLoading ? <LoadingState /> :
        casesError ? <ErrorState message={casesError} onRetry={reloadCases} /> : (
          <ul className="px-4 space-y-2">
            {(casesData?.items || []).slice(0, 20).map(c => (
              <li key={c.case_id} className="bg-gray-800 rounded-xl p-3 text-xs space-y-1">
                <div className="flex justify-between items-center gap-2">
                  <span className="font-mono text-[9px] text-gray-600">{c.case_id}</span>
                  <span className="text-green-400 font-mono text-[9px]">
                    {Math.round(c.base_confidence * 100)}%
                  </span>
                </div>
                <p className="text-gray-300 line-clamp-2">{c.case_text}</p>
                <p className="text-green-300 font-semibold text-[10px]">{c.final_diagnosis}</p>
                <span className="inline-block text-[9px] bg-gray-700 rounded px-1.5 py-0.5 text-gray-400">
                  {c.symptom_category} · {c.model}
                </span>
              </li>
            ))}
          </ul>
        )
      )}
    </div>
  )
}
