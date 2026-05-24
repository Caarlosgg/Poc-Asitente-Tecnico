import { useState } from 'react'

/**
 * Barra de entrada de texto del chat.
 * Enter envía, Shift+Enter nueva línea.
 */
export default function InputBar({ onSend, disabled, placeholder = 'Escribe un mensaje...' }) {
  const [text, setText] = useState('')

  function handleSend() {
    const trimmed = text.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setText('')
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const canSend = !disabled && text.trim().length > 0

  return (
    <div className="flex items-end gap-2 px-3 py-2.5 bg-gray-900/95 border-t border-gray-800">
      <textarea
        className="flex-1 bg-gray-800 text-gray-100 rounded-xl px-4 py-2.5 text-sm resize-none
                   border border-gray-700/60 transition-all duration-150
                   focus:outline-none focus:border-blue-600/70 focus:ring-1 focus:ring-blue-600/20
                   placeholder:text-gray-600 min-h-[42px] max-h-[120px] leading-relaxed"
        rows={1}
        value={text}
        onChange={e => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder={disabled ? 'Esperando respuesta...' : placeholder}
        maxLength={2000}
      />
      <button
        onClick={handleSend}
        disabled={!canSend}
        className={`flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-sm font-semibold
          transition-all duration-150 whitespace-nowrap shadow-md
          ${
            canSend
              ? 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-900/40 active:scale-95'
              : 'bg-gray-800 text-gray-600 cursor-not-allowed border border-gray-700'
          }`}
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 19V5m0 0l-7 7m7-7l7 7" />
        </svg>
        Enviar
      </button>
    </div>
  )
}
