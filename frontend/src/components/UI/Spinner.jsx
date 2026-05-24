/**
 * Spinner de carga con mensaje opcional.
 */
export default function Spinner({ message = 'Procesando...' }) {
  return (
    <div className="flex items-center gap-3 px-4 py-3">
      <div className="w-5 h-5 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
      <span className="text-gray-400 text-sm">{message}</span>
    </div>
  )
}
