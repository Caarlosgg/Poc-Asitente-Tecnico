import { useState } from 'react'
import ChatContainer from './components/Chat/ChatContainer'
import FeedbackModal from './components/UI/FeedbackModal'
import PhaseBar from './components/UI/PhaseBar'
import HealthIndicator from './components/UI/HealthIndicator'
import LeftNavSidebar from './components/Analytics/LeftNavSidebar'

export default function App() {
  const [showFeedback, setShowFeedback] = useState(false)
  const [sessionId, setSessionId]       = useState(null)
  const [vehicleInfo, setVehicleInfo]   = useState(null) // { vin, model }
  const [phase, setPhase]               = useState('vin') // 'vin'|'menu'|'diagnosis'|'feedback'

  const handleRequestFeedback = (sid) => {
    setSessionId(sid)
    setShowFeedback(true)
    setPhase('feedback')
  }

  const handleFeedbackClose = () => {
    setShowFeedback(false)
    window.location.reload()
  }

  return (
    <div className="h-screen bg-gray-950 flex flex-col overflow-hidden">

      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <header className="bg-gray-900 border-b border-gray-800 px-4 py-2.5 flex items-center gap-3 shrink-0 z-10">
        {/* Logo + title */}
        <div className="flex items-center gap-2.5 shrink-0">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center text-base shadow-md shadow-blue-900/40">
            🏍️
          </div>
          <div>
            <h1 className="text-sm font-bold text-gray-100 leading-tight tracking-tight">
              Asistente Técnico
            </h1>
            <p className="text-[10px] text-gray-600 leading-tight">Sistema de Diagnóstico Guiado</p>
          </div>
        </div>

        {/* Divider */}
        <div className="w-px h-6 bg-gray-800 mx-1 shrink-0" />

        {/* Vehicle badge */}
        {vehicleInfo ? (
          <div className="flex items-center gap-2 bg-gray-800/80 rounded-lg px-2.5 py-1.5 border border-gray-700/50">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-40" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500" />
            </span>
            <span className="text-xs text-green-300 font-semibold">{vehicleInfo.model}</span>
            {vehicleInfo.vin && (
              <span className="text-[10px] text-gray-500 font-mono">{vehicleInfo.vin}</span>
            )}
          </div>
        ) : (
          <div className="flex items-center gap-1.5 text-xs text-gray-600">
            <span className="w-2 h-2 rounded-full bg-gray-700" />
            <span>Sin vehículo identificado</span>
          </div>
        )}

        {/* Right side */}
        <div className="ml-auto flex items-center gap-2">
          <HealthIndicator />
          <div className="w-px h-5 bg-gray-800" />
          <span className="text-[10px] text-gray-700 font-mono bg-gray-900 border border-gray-800 rounded px-1.5 py-0.5">
            v1.0
          </span>
        </div>
      </header>

      {/* ── Body: left nav + chat area ──────────────────────────────────────── */}
      <div className="flex flex-1 overflow-hidden">

        {/* Left analytics nav */}
        <LeftNavSidebar />

        {/* Right: phase bar + chat */}
        <div className="flex flex-col flex-1 overflow-hidden">
          <PhaseBar phase={phase} />
          <ChatContainer
            onRequestFeedback={handleRequestFeedback}
            onVehicleIdentified={(info) => {
              setVehicleInfo(info)
              setPhase('menu')
            }}
            onPhaseChange={setPhase}
          />
        </div>
      </div>

      {/* ── Feedback modal ──────────────────────────────────────────────────── */}
      {showFeedback && (
        <FeedbackModal
          sessionId={sessionId}
          onClose={handleFeedbackClose}
        />
      )}
    </div>
  )
}

