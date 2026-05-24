import { useEffect, useRef, useMemo, useState } from 'react'
import { useSession } from '../../hooks/useSession'
import { useChat } from '../../hooks/useChat'
import { MESSAGE_TYPES, ROLES } from '../../utils/messageTypes'
import MessageBubble from './MessageBubble'
import RouteHeader from './RouteHeader'
import QuickReplies from './QuickReplies'
import MenuOptions from './MenuOptions'
import InputBar from './InputBar'
import Spinner from '../UI/Spinner'
import ErrorMessage from '../UI/ErrorMessage'
import SessionSummaryPanel from '../UI/SessionSummaryPanel'

// F4: Barra de progreso estimada del árbol de diagnóstico
// La confianza aumenta con cada pregunta respondida (estimamos 7 pasos máximo)
const TREE_MAX_STEPS = 7

function TreeProgressBar({ stepNumber }) {
  const pct = Math.min(Math.round((stepNumber / TREE_MAX_STEPS) * 90), 90)
  return (
    <div className="mx-3 mb-1 px-3 py-2 rounded-xl bg-green-950/20 border border-green-900/30">
      <div className="flex justify-between text-[10px] text-gray-500 mb-1">
        <span className="flex items-center gap-1">
          <span>🌳</span>
          <span>Progreso del diagnóstico guiado</span>
        </span>
        <span className="font-mono text-green-400">Paso {stepNumber}</span>
      </div>
      <div className="w-full h-1 bg-gray-700 rounded-full overflow-hidden">
        <div
          className="h-full bg-green-500 rounded-full transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

/**
 * Contenedor principal del chat.
 * Gestiona el ciclo completo: sesión → mensajes → respuestas → opciones.
 * Detecta cambios de ruta (A/B/C) e inserta RouteHeader inline.
 */
export default function ChatContainer({ onRequestFeedback, onVehicleIdentified, onPhaseChange }) {
  const { sessionId, loading: sessionLoading, error: sessionError, createNewSession } = useSession()
  const { messages, loading: chatLoading, error: chatError, send, addMessage, clearError } = useChat(sessionId)
  const messagesEndRef = useRef(null)
  const initializedRef = useRef(false)
  const [showSummary, setShowSummary] = useState(false)

  // Inicializar sesión y mostrar mensaje de bienvenida
  useEffect(() => {
    if (sessionId && !initializedRef.current && messages.length === 0) {
      initializedRef.current = true
      ;(async () => {
        const result = await createNewSession()
        if (result) {
          const { welcomeMessage } = result
          addMessage(
            ROLES.ASSISTANT,
            welcomeMessage.message,
            welcomeMessage.message_type,
            welcomeMessage.options,
          )
        }
      })()
    }
  }, [sessionId])

  // Detectar cuando se identifica el vehículo y notificar al padre
  useEffect(() => {
    if (!onVehicleIdentified) return
    const menuMsg = messages.find(m => m.messageType === MESSAGE_TYPES.MENU)
    if (menuMsg) {
      const vinMatch = menuMsg.content.match(/Vehículo identificado: ([^.(]+)/)
      if (vinMatch) {
        onVehicleIdentified({ model: vinMatch[1].trim(), vin: '' })
      }
    }
  }, [messages])

  // Derivar fase actual y notificar al padre para PhaseBar
  useEffect(() => {
    if (!onPhaseChange) return
    const hasDiagnosis = messages.some(m => m.messageType === MESSAGE_TYPES.DIAGNOSIS)
    const hasMenu = messages.some(m => m.messageType === MESSAGE_TYPES.MENU)
    const hasVin = messages.some(m => m.route != null)  // primera respuesta post-VIN

    if (hasDiagnosis) onPhaseChange('diagnosis')
    else if (hasMenu) onPhaseChange('menu')
    else if (messages.length > 1) onPhaseChange('vin')
    else onPhaseChange('vin')
  }, [messages])

  // Auto-scroll al último mensaje
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, chatLoading])

  // Construir lista de items del chat: mensajes + RouteHeaders intercalados
  const chatItems = useMemo(() => {
    const items = []
    let lastRoute = null
    let lastSymptom = null

    for (const msg of messages) {
      // Detectar cambio de ruta en mensajes del asistente
      if (msg.role === ROLES.ASSISTANT && msg.route && msg.route !== lastRoute) {
        const symptomFromContent = msg.messageType === MESSAGE_TYPES.QUESTION
          ? null  // el árbol no lleva síntoma en el mensaje
          : null
        items.push({ type: 'route-header', route: msg.route, symptom: lastSymptom, id: `rh-${msg.id}` })
        lastRoute = msg.route
      }

      // Detectar síntoma seleccionado (cuando el asistente muestra el árbol)
      if (msg.messageType === MESSAGE_TYPES.QUESTION && msg.route === 'tree') {
        // El síntoma viene implícito — lo dejamos null para mostrar el label genérico
      }

      items.push({ type: 'message', msg })
    }
    return items
  }, [messages])

  const lastMessage = messages[messages.length - 1]
  const lastOptions = lastMessage?.options || null
  const lastMessageType = lastMessage?.messageType
  const lastSuggestsTree = lastMessage?.suggestsTree || null

  const showMenu = lastMessageType === MESSAGE_TYPES.MENU && !chatLoading
  const showQuickReplies =
    (lastMessageType === MESSAGE_TYPES.QUESTION ||
      lastMessageType === MESSAGE_TYPES.DIAGNOSIS ||
      (lastMessageType === MESSAGE_TYPES.TEXT && lastOptions)) &&
    !chatLoading

  async function handleSend(message, displayText) {
    clearError()

    if (message === 'finish' && sessionId) {
      onRequestFeedback(sessionId)
      if (onPhaseChange) onPhaseChange('feedback')
      return
    }

    await send(message, displayText)
  }

  // Manejar sugerencia de reconducción al árbol
  async function handleAcceptReconduction(treeId) {
    clearError()
    // Enviamos el id del árbol como si el usuario lo seleccionara
    const treeIdToOption = {
      'AK550_MOTOR_V1':    { id: 'symptom_motor',    label: '🔧 Paradas de motor' },
      'AK550_CELP_V1':     { id: 'symptom_celp',     label: '⚠️ Testigo CELP encendido' },
      'AK550_ARRANQUE_V1': { id: 'symptom_arranque', label: '🔩 Problemas de arranque' },
      'AK550_CONSUMO_V1':  { id: 'symptom_consumo',  label: '⛽ Consumo excesivo' },
      'XCITING_MOTOR_V1':  { id: 'symptom_motor',    label: '🔧 Paradas de motor' },
    }
    const opt = treeIdToOption[treeId]
    if (opt) await send(opt.id, opt.label)
  }

  if (sessionLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <Spinner message="Iniciando sesión..." />
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col max-w-3xl mx-auto w-full overflow-hidden">
      {/* Lista de mensajes con RouteHeaders intercalados — min-h-0 permite overflow scroll real */}
      <div className="flex-1 overflow-y-auto min-h-0 px-3 py-4 space-y-1">
        {chatItems.map(item =>
          item.type === 'route-header'
            ? <RouteHeader key={item.id} route={item.route} symptom={item.symptom} />
            : <MessageBubble key={item.msg.id} message={item.msg} />
        )}

        {/* Indicador de escritura */}
        {chatLoading && (
          <div className="flex justify-start mb-3">
            <div className="flex gap-2 items-end">
              <div className="w-7 h-7 rounded-full bg-gray-700 text-gray-300 flex items-center justify-center text-sm shrink-0">🔧</div>
              <div className="bg-gray-700 rounded-2xl rounded-tl-sm px-4 py-3.5 inline-flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.32s]" />
                <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.16s]" />
                <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" />
              </div>
            </div>
          </div>
        )}

        {(chatError || sessionError) && (
          <ErrorMessage
            message={chatError || sessionError}
            onRetry={chatError ? clearError : createNewSession}
          />
        )}

        {/* Card de reconducción al árbol (Ruta C → Ruta A) */}
        {lastSuggestsTree && !chatLoading && (
          <div className="mx-1 my-2 p-3 rounded-xl border border-green-700/40 bg-green-950/20 flex items-start gap-3">
            <span className="text-xl shrink-0">🌳</span>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-green-400 mb-0.5">Diagnóstico guiado disponible</p>
              <p className="text-xs text-gray-400 leading-relaxed">
                Este síntoma tiene un árbol de diagnóstico estructurado. ¿Quieres seguirlo para obtener una causa más precisa?
              </p>
              <div className="flex gap-2 mt-2">
                <button
                  onClick={() => handleAcceptReconduction(lastSuggestsTree)}
                  className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-green-700 hover:bg-green-600 text-white transition-colors"
                >
                  Sí, usar árbol de diagnóstico
                </button>
                <button
                  onClick={() => handleSend('menu', 'Volver al menú')}
                  className="text-xs px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 border border-gray-700 transition-colors"
                >
                  No, mantener resultado
                </button>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* F4: Indicador de progreso del árbol de diagnóstico */}
      {lastMessageType === MESSAGE_TYPES.QUESTION && lastMessage?.route === 'tree' && !chatLoading && (
        <TreeProgressBar stepNumber={lastMessage?.stepNumber || 1} />
      )}

      {/* Divisor antes de opciones */}
      {(showMenu || showQuickReplies) && (
        <div className="border-t border-gray-800 mx-3" />
      )}

      {/* Opciones interactivas */}
      {showMenu && lastOptions && (
        <MenuOptions
          options={lastOptions}
          onSelect={(id, label) => handleSend(id, label)}
          disabled={chatLoading}
        />
      )}

      {showQuickReplies && !showMenu && lastOptions && (
        <QuickReplies
          options={lastOptions}
          onSelect={(id, label) => handleSend(id, label)}
          disabled={chatLoading}
        />
      )}

      {/* F1: Botón "Ver resumen de sesión" tras diagnóstico */}
      {lastMessageType === MESSAGE_TYPES.DIAGNOSIS && !chatLoading && sessionId && (
        <div className="px-4 pb-2 flex justify-center">
          <button
            onClick={() => setShowSummary(true)}
            className="text-xs text-gray-500 hover:text-gray-300 border border-gray-800 hover:border-gray-600 rounded-lg px-3 py-1.5 transition-colors flex items-center gap-1.5"
          >
            <span>📋</span> Ver resumen de sesión
          </button>
        </div>
      )}

      {/* F1: Panel de resumen de sesión */}
      {showSummary && sessionId && (
        <SessionSummaryPanel
          sessionId={sessionId}
          onClose={() => setShowSummary(false)}
        />
      )}

      {/* Barra de entrada */}
      <InputBar
        onSend={(text) => handleSend(text)}
        disabled={chatLoading || !!sessionError}
        placeholder="Introduce el bastidor o escribe tu consulta..."
      />
    </div>
  )
}
