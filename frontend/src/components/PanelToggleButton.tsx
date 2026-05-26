import { MaterialIcon } from './MaterialIcon'

interface PanelToggleButtonProps {
  icon: 'chevron_left' | 'chevron_right' | 'close'
  label: string
  testId?: string
  onClick: () => void
}

/** Panel kenarı küçült / genişlet — siyah, net ikon. */
export function PanelToggleButton({
  icon,
  label,
  testId,
  onClick,
}: PanelToggleButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-[var(--color-on-surface)] transition-colors hover:bg-[var(--color-surface-container)]"
      aria-label={label}
      data-testid={testId}
    >
      <MaterialIcon
        name={icon}
        size={22}
        weight={500}
        className="text-[var(--color-on-surface)]"
      />
    </button>
  )
}
