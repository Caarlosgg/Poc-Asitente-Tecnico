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
import SymptomHeatMap from './SymptomHeatMap'
import PdfExport from './PdfExport'

// ── Generic data hook (lazy: only fetches when enabled=true) ─────────────────
function useApiData(fetcher, enabled = true) {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const load = useCallback(() => {
    if (!enabled) return
    setLoading(true)
    setError(null)
    fetcher()
      .then(setData)
      .catch(e => setError(e.message || 'Error'))
      .finally(() => setLoading(false))
  }, [enabled])

  useEffect(() => { if (enabled) load() }, [enabled])
  return { data, loading, error, reload: load }
}

// ── Tiny shared UI ────────────────────────────────────────────────────────────
function SectionLabel({ children }) {
  return (
    <p className="text-[9px] font-bold text-gray-600 uppercase tracking-widest mt-3 mb-1">
      {children}
    </p>
  )
}

function StatRow({ label, value, color = 'text-gray-300' }) {
  return (
    <div className="flex justify-between items-center py-[3px]">
      <span className="text-[11px] text-gray-500 truncate pr-2">{label}</span>
      <span className={`text-[11px] font-mono font-semibold shrink-0 ${color}`}>{value ?? '—'}</span>
    </div>
  )
}

function LoadingDots() {
  return (
    <div className="flex items-center gap-1 py-3">
      {[0, 150, 300].map(d => (
        <div
          key={d}
          className="w-1.5 h-1.5 rounded-full bg-gray-600 animate-bounce"
          style={{ animationDelay: `${d}ms` }}
        />
      ))}
    </div>
  )
}

function EmptyState({ text }) {
  return <p className="text-[11px] text-gray-700 py-3 text-center">{text}</p>
}

// ── Section content ───────────────────────────────────────────────────────────
function MetricsContent({ open }) {
  const { data, loading } = useApiData(getMetrics, open)
  if (loading) return <LoadingDots />
  if (!data) return <EmptyState text="Sin datos" />

  return (
    <div>
      <SectionLabel>Sesiones</SectionLabel>
      <StatRow label="Total"           value={data.total_sessions}      color="text-blue-400" />
      <StatRow label="Completadas"     value={data.completed_sessions}   color="text-green-400" />
      <StatRow label="Tasa de éxito"   value={data.success_rate != null ? `${Math.round(data.success_rate * 100)}%` : null} color="text-green-400" />
      <StatRow label="Pasos promedio"  value={data.avg_steps}           color="text-yellow-400" />
      <StatRow label="Duración media"  value={data.avg_duration_seconds != null ? `${data.avg_duration_seconds}s` : null} />

      <SectionLabel>Módulos</SectionLabel>
      <StatRow label="🌳 Árbol guiado" value={data.module_usage?.tree ?? 0}      color="text-green-400" />
      <StatRow label="📋 FAQ"          value={data.module_usage?.faq ?? 0}       color="text-blue-400" />
      <StatRow label="📂 Historial"    value={data.module_usage?.free_text ?? 0} color="text-purple-400" />

      <SectionLabel>Feedback</SectionLabel>
      <StatRow label="👍 Positivo" value={data.positive_feedback} color="text-green-400" />
      <StatRow label="👎 Negativo" value={data.negative_feedback} color="text-red-400" />

      {data.top_diagnoses?.length > 0 && (
        <>
          <SectionLabel>Top diagnósticos</SectionLabel>
          {data.top_diagnoses.map((d, i) => (
            <div key={i} className="flex items-start gap-1.5 py-[3px]">
              <span className="text-[9px] text-gray-700 font-mono w-3 shrink-0">{i + 1}.</span>
              <span className="text-[11px] text-gray-400 flex-1 leading-snug">{d.diagnosis}</span>
              <span className="text-[11px] text-green-500 font-mono shrink-0">{d.count}×</span>
            </div>
          ))}
        </>
      )}
    </div>
  )
}

function SessionsContent({ open }) {
  const { data, loading } = useApiData(() => getAnalyticsSessions(10), open)
  if (loading) return <LoadingDots />
  if (!data?.items?.length) return <EmptyState text="Sin sesiones aún" />

  return (
    <div className="space-y-1.5">
      {data.items.map(s => (
        <div key={s.session_id} className="bg-gray-800/50 border border-gray-800 rounded-lg p-2">
          <div className="flex justify-between items-center gap-1">
            <span className="text-[11px] text-green-300 font-semibold truncate">{s.model || '—'}</span>
            <span className={`text-[9px] px-1.5 py-0.5 rounded-full shrink-0 ${
              s.status === 'closed'
                ? 'bg-green-900/40 text-green-400'
                : 'bg-yellow-900/40 text-yellow-400'
            }`}>
              {s.status}
            </span>
          </div>
          <div className="text-[9px] text-gray-700 font-mono truncate mt-0.5">
            {s.session_id.slice(0, 18)}…
          </div>
          {s.final_result && (
            <div className="text-[10px] text-gray-400 truncate mt-0.5">{s.final_result}</div>
          )}
          <div className="text-[9px] text-gray-600 mt-0.5">
            {s.total_steps} pasos{s.duration_seconds != null ? ` · ${s.duration_seconds}s` : ''}
          </div>
        </div>
      ))}
    </div>
  )
}

function DiagnosesContent({ open }) {
  const { data, loading } = useApiData(getAnalyticsDiagnoses, open)
  if (loading) return <LoadingDots />
  if (!data?.items?.length) return <EmptyState text="Sin diagnósticos aún" />

  const max = Math.max(...data.items.map(d => d.count), 1)

  return (
    <div className="space-y-2.5">
      {data.items.map((d, i) => (
        <div key={i}>
          <div className="flex justify-between items-baseline gap-1 mb-0.5">
            <span className="text-[10px] text-gray-400 leading-snug flex-1">{d.diagnosis}</span>
            <span className="text-[10px] text-green-400 font-mono shrink-0">{d.count}×</span>
          </div>
          <div className="w-full h-1 bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-green-700 to-green-500 rounded-full transition-all"
              style={{ width: `${Math.round((d.count / max) * 100)}%` }}
            />
          </div>
          {d.model && <p className="text-[9px] text-gray-700 mt-0.5">{d.model}</p>}
        </div>
      ))}
    </div>
  )
}

function FeedbackContent({ open }) {
  const { data, loading } = useApiData(() => getAnalyticsFeedback(10), open)
  if (loading) return <LoadingDots />
  if (!data) return <EmptyState text="Sin feedback aún" />

  return (
    <div>
      {data.total > 0 && (
        <>
          <SectionLabel>Resumen</SectionLabel>
          <StatRow label="Total" value={data.total} />
          <StatRow label="👍 Positivo" value={data.positive} color="text-green-400" />
          <StatRow label="👎 Negativo" value={data.negative} color="text-red-400" />
          <StatRow
            label="Tasa positiva"
            value={`${Math.round((data.positive_rate || 0) * 100)}%`}
            color="text-green-400"
          />
          <SectionLabel>Valoraciones recientes</SectionLabel>
        </>
      )}
      <div className="space-y-1.5">
        {(data.items || []).map((f, i) => (
          <div key={i} className="bg-gray-800/50 border border-gray-800 rounded-lg p-2">
            <div className="flex items-center gap-1.5">
              <span className="text-sm">{f.useful ? '👍' : '👎'}</span>
              <span className={`text-[10px] font-semibold ${f.useful ? 'text-green-400' : 'text-red-400'}`}>
                {f.useful ? 'Útil' : 'No útil'}
              </span>
            </div>
            {f.comment && (
              <p className="text-[10px] text-gray-500 italic mt-0.5 leading-snug">"{f.comment}"</p>
            )}
            <p className="text-[9px] text-gray-700 font-mono truncate mt-0.5">
              {f.session_id?.slice(0, 18)}…
            </p>
          </div>
        ))}
        {!data.items?.length && <EmptyState text="Sin valoraciones aún" />}
      </div>
    </div>
  )
}

function KnowledgeContent({ open }) {
  const { data: trees }                       = useApiData(getKnowledgeTrees, open)
  const { data: faqs,  loading: faqsL  }     = useApiData(getKnowledgeFaqs, open)
  const { data: cases, loading: casesL }     = useApiData(getKnowledgeCases, open)
  const [sub, setSub] = useState('trees')

  const subBtns = [
    { id: 'trees', label: `🌳 Árboles (${trees?.total ?? '…'})` },
    { id: 'faqs',  label: `📋 FAQs (${faqs?.total ?? '…'})` },
    { id: 'cases', label: `📂 Casos (${cases?.total ?? '…'})` },
  ]

  return (
    <div>
      {/* Sub-nav pills */}
      <div className="flex flex-wrap gap-1 mb-2">
        {subBtns.map(b => (
          <button
            key={b.id}
            onClick={() => setSub(b.id)}
            className={`text-[9px] px-2 py-0.5 rounded-full font-semibold transition-colors ${
              sub === b.id
                ? 'bg-blue-900 text-blue-300 border border-blue-700'
                : 'text-gray-600 hover:text-gray-400 border border-gray-800'
            }`}
          >
            {b.label}
          </button>
        ))}
      </div>

      {sub === 'trees' && (
        trees ? (
          <div className="space-y-1.5">
            {trees.items.map(t => (
              <div key={t.tree_id} className="bg-gray-800/50 border border-gray-800 rounded-lg p-2">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="text-[10px] text-green-300 font-semibold">{t.tree_id}</div>
                    <div className="text-[9px] text-gray-600">{t.model} · {t.symptom}</div>
                  </div>
                  <span className="text-[9px] text-gray-600 shrink-0 ml-1">{t.node_count} nodos</span>
                </div>
              </div>
            ))}
          </div>
        ) : <LoadingDots />
      )}

      {sub === 'faqs' && (
        faqsL ? <LoadingDots /> : (
          <div className="space-y-1.5">
            {(faqs?.items || []).slice(0, 10).map(f => (
              <div key={f.faq_id} className="bg-gray-800/50 border border-gray-800 rounded-lg p-2">
                <div className="text-[10px] text-gray-300 font-semibold leading-snug">{f.question}</div>
                <div className="text-[9px] text-gray-600 mt-0.5">
                  {f.category} · {f.model || 'Todos'} · {f.usage_count}× usado
                </div>
              </div>
            ))}
            {!faqs?.items?.length && <EmptyState text="Sin FAQs" />}
          </div>
        )
      )}

      {sub === 'cases' && (
        casesL ? <LoadingDots /> : (
          <div className="space-y-1.5">
            {(cases?.items || []).slice(0, 10).map(c => (
              <div key={c.case_id} className="bg-gray-800/50 border border-gray-800 rounded-lg p-2">
                <div className="flex justify-between items-center">
                  <span className="text-[9px] text-gray-700 font-mono">{c.case_id}</span>
                  <span className="text-[9px] text-green-500 font-mono">{Math.round(c.base_confidence * 100)}%</span>
                </div>
                <div className="text-[10px] text-green-300 font-semibold truncate mt-0.5">{c.final_diagnosis}</div>
                <div className="text-[9px] text-gray-600">{c.model} · {c.symptom_category}</div>
              </div>
            ))}
            {!cases?.items?.length && <EmptyState text="Sin casos" />}
          </div>
        )
      )}
    </div>
  )
}

// ── Accordion section ─────────────────────────────────────────────────────────
function HeatMapContent({ open }) {
  if (!open) return null
  return <SymptomHeatMap />
}

function PdfExportContent({ open }) {
  if (!open) return null
  return <PdfExport />
}

const SECTION_CONTENT = {
  metrics:   MetricsContent,
  sessions:  SessionsContent,
  diagnoses: DiagnosesContent,
  feedback:  FeedbackContent,
  knowledge: KnowledgeContent,
  heatmap:   HeatMapContent,
  export:    PdfExportContent,
}

function AccordionSection({ id, icon, label, isOpen, onToggle }) {
  const Content = SECTION_CONTENT[id]
  return (
    <div className="border-b border-gray-800/60">
      <button
        onClick={onToggle}
        className={`w-full flex items-center gap-2.5 px-3 py-2.5 transition-colors text-left group
          ${isOpen ? 'bg-gray-800/30' : 'hover:bg-gray-800/20'}`}
      >
        <span className="text-base shrink-0">{icon}</span>
        <span className={`text-xs font-semibold flex-1 transition-colors
          ${isOpen ? 'text-gray-100' : 'text-gray-400 group-hover:text-gray-300'}`}>
          {label}
        </span>
        <svg
          className={`w-3 h-3 text-gray-600 transition-transform duration-200 shrink-0
            ${isOpen ? 'rotate-90' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
        </svg>
      </button>

      {isOpen && (
        <div className="px-3 pb-3 pt-1 animate-in">
          <Content open={isOpen} />
        </div>
      )}
    </div>
  )
}

// ── Collapsed icon bar ────────────────────────────────────────────────────────
const SECTIONS = [
  { id: 'metrics',   icon: '📊', label: 'Métricas del sistema' },
  { id: 'sessions',  icon: '🗂️',  label: 'Sesiones recientes' },
  { id: 'diagnoses', icon: '🔎', label: 'Diagnósticos' },
  { id: 'feedback',  icon: '💬', label: 'Feedback' },
  { id: 'knowledge', icon: '📚', label: 'Base de conocimiento' },
  { id: 'heatmap',   icon: '🌡️', label: 'Mapa de calor de síntomas' },
  { id: 'export',    icon: '📄', label: 'Exportar informe PDF' },
]

function CollapsedBar({ onExpand, onExpandSection }) {
  return (
    <aside className="w-11 bg-gray-900 border-r border-gray-800 flex flex-col items-center pt-3 pb-3 gap-0.5 shrink-0">
      {SECTIONS.map(s => (
        <button
          key={s.id}
          onClick={() => onExpandSection(s.id)}
          title={s.label}
          className="w-9 h-9 flex items-center justify-center rounded-lg text-base text-gray-600
                     hover:bg-gray-800 hover:text-gray-300 transition-colors"
        >
          {s.icon}
        </button>
      ))}
      <div className="mt-auto">
        <button
          onClick={onExpand}
          title="Expandir panel"
          className="w-9 h-8 flex items-center justify-center text-gray-700 hover:text-gray-500 transition-colors"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </aside>
  )
}

// ── Main export ───────────────────────────────────────────────────────────────
export default function LeftNavSidebar() {
  const [collapsed, setCollapsed]       = useState(false)
  const [openSections, setOpenSections] = useState(new Set(['metrics']))

  const toggleSection = (id) => {
    setOpenSections(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const expandTo = (id) => {
    setCollapsed(false)
    setOpenSections(new Set([id]))
  }

  if (collapsed) {
    return (
      <CollapsedBar
        onExpand={() => setCollapsed(false)}
        onExpandSection={expandTo}
      />
    )
  }

  return (
    <aside className="w-72 bg-gray-900 border-r border-gray-800 flex flex-col overflow-hidden shrink-0">
      {/* Header */}
      <div className="flex items-center gap-2 px-3 py-2.5 border-b border-gray-800 shrink-0 bg-gray-900/80">
        <span className="text-base">📊</span>
        <span className="text-xs font-bold text-gray-200 flex-1">Panel de Analítica</span>
        <button
          onClick={() => setCollapsed(true)}
          title="Contraer"
          className="w-7 h-7 flex items-center justify-center rounded-lg text-gray-600
                     hover:bg-gray-800 hover:text-gray-400 transition-colors"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      </div>

      {/* Refresh hint */}
      <div className="px-3 py-1.5 bg-gray-900 border-b border-gray-800/50 shrink-0">
        <p className="text-[9px] text-gray-700">
          Los datos se cargan al abrir cada sección.
        </p>
      </div>

      {/* Accordion */}
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {SECTIONS.map(s => (
          <AccordionSection
            key={s.id}
            {...s}
            isOpen={openSections.has(s.id)}
            onToggle={() => toggleSection(s.id)}
          />
        ))}
      </div>

      {/* Footer */}
      <div className="px-3 py-2 border-t border-gray-800 shrink-0">
        <p className="text-[9px] text-gray-700 font-mono">POC Asistente Técnico v1.0</p>
      </div>
    </aside>
  )
}
