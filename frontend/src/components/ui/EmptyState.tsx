interface EmptyStateProps {
  title: string
  message: string
  actionLabel?: string
  onAction?: () => void
}

function EmptyState({ title, message, actionLabel, onAction }: EmptyStateProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-10 text-center">
      <h3 className="text-lg font-semibold text-gray-800 mb-2">{title}</h3>
      <p className="text-gray-500 mb-6">{message}</p>
      {actionLabel && onAction && (
        <button onClick={onAction} className="bg-blue-600 text-white rounded-md px-4 py-2 hover:bg-blue-700">
          {actionLabel}
        </button>
      )}
    </div>
  )
}

export default EmptyState
