interface ErrorToastProps {
  message: string | null
  onDismiss: () => void
}

/** Kullanıcıya kısa süreli hata mesajı gösterir. */
export function ErrorToast({ message, onDismiss }: ErrorToastProps) {
  if (!message) return null

  return (
    <div
      role="alert"
      className="fixed bottom-4 left-1/2 z-50 flex max-w-md -translate-x-1/2 items-center gap-3 rounded-lg border border-[var(--color-outline)] bg-[var(--color-surface)] px-4 py-3 shadow-md"
    >
      <p className="flex-1 text-sm text-[var(--color-error)]">{message}</p>
      <button
        type="button"
        onClick={onDismiss}
        className="text-sm font-medium text-[var(--color-on-surface-variant)] hover:text-[var(--color-on-surface)]"
        aria-label="Kapat"
      >
        Kapat
      </button>
    </div>
  )
}
