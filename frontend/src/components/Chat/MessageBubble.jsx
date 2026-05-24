import DiagnosisResult from '../Diagnosis/DiagnosisResult'
import { ROLES, MESSAGE_TYPES } from '../../utils/messageTypes'

/** Formatea timestamp ISO a HH:MM */
function formatTime(iso) {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ''
  }
}

/** Avatar del rol */
function RoleAvatar({ isUser }) {
  return (
    <div
      className={`w-7 h-7 rounded-full flex items-center justify-center text-sm shrink-0 shadow-sm
        ${isUser
          ? 'bg-gradient-to-br from-blue-500 to-blue-700 text-white'
          : 'bg-gradient-to-br from-gray-700 to-gray-800 text-gray-300 border border-gray-700'
        }`}
    >
      {isUser ? '👤' : '🔧'}
    </div>
  )
}

/** Badge del paso actual en árbol de diagnóstico */
function StepBadge({ stepNumber }) {
  if (!stepNumber) return null
  return (
    <span className="inline-flex items-center gap-1 text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-green-900/40 border border-green-700/40 text-green-400 mb-1.5">
      <svg className="w-2.5 h-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
      Paso {stepNumber}
    </span>
  )
}

/** Pill del tipo de ruta */
const ROUTE_BADGE = {
  tree:  { label: '🌳 Árbol guiado', cls: 'bg-green-900/30 border-green-800/60 text-green-500' },
  faq:   { label: '📋 FAQ',          cls: 'bg-blue-900/30 border-blue-800/60 text-blue-400' },
  other: { label: '🔍 Historial',    cls: 'bg-purple-900/30 border-purple-800/60 text-purple-400' },
}

function RoutePill({ route }) {
  const cfg = ROUTE_BADGE[route]
  if (!cfg) return null
  return (
    <span className={`inline-flex text-[9px] font-semibold px-1.5 py-0.5 rounded-full border ${cfg.cls}`}>
      {cfg.label}
    </span>
  )
}

/**
 * Burbuja de mensaje individual.
 * Entrada con fade-in suave. Renderiza distinto según rol y tipo.
 */
export default function MessageBubble({ message }) {
  const isUser     = message.role === ROLES.USER
  const isError    = message.messageType === MESSAGE_TYPES.ERROR
  const isQuestion = message.messageType === MESSAGE_TYPES.QUESTION
  const time       = formatTime(message.timestamp)

  return (
    <div
      className={`flex gap-2 mb-3 animate-fade-in
        ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      <RoleAvatar isUser={isUser} />

      <div className={`flex flex-col max-w-[78%] ${isUser ? 'items-end' : 'items-start'}`}>
        {/* Step badge (solo preguntas del árbol) */}
        {!isUser && isQuestion && <StepBadge stepNumber={message.stepNumber} />}

        {/* Burbuja principal */}
        {message.messageType === MESSAGE_TYPES.DIAGNOSIS && message.diagnosis ? (
          <DiagnosisResult diagnosis={message.diagnosis} message={message.content} />
        ) : (
          <div
            className={`px-4 py-2.5 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap shadow-sm
              ${isUser
                ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-tr-sm'
                : isError
                ? 'bg-red-950/80 text-red-300 border border-red-800/60 rounded-tl-sm'
                : isQuestion
                ? 'bg-gray-800 text-gray-100 rounded-tl-sm border border-green-800/20 ring-1 ring-green-900/20'
                : 'bg-gray-800/90 text-gray-100 rounded-tl-sm border border-gray-700/50'
              }`}
          >
            {message.content}
          </div>
        )}

        {/* Footer: hora + ruta */}
        <div className={`flex items-center gap-2 mt-1 px-0.5 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
          {time && <span className="text-[10px] text-gray-700">{time}</span>}
          {!isUser && message.route && <RoutePill route={message.route} />}
        </div>
      </div>
    </div>
  )
}

