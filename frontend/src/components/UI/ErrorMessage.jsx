/**
 * Mensaje de error con opción de reintentar.
 */
export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="flex flex-col gap-2 px-4 py-3 bg-red-900/30 border border-red-700 rounded-lg mx-4 my-2">
      <p className="text-red-300 text-sm">
        <span className="font-semibold">⚠ Error:</span> {message}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="self-start text-xs text-red-400 hover:text-red-200 underline"
        >
          Reintentar
        </button>
      )}
    </div>
  )
}
