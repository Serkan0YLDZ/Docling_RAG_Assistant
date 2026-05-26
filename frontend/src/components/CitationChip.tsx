interface CitationChipProps {
  label: string
  onClick: () => void
}

/** Stitch kaynak referans chip'i ([1], [2]). */
export function CitationChip({ label, onClick }: CitationChipProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="source-chip mx-0.5 inline-flex cursor-pointer items-center justify-center rounded-full border border-[var(--color-citation-border)] bg-[var(--color-citation-bg)] px-2 py-[2px] text-xs font-medium text-[var(--color-primary)] transition-all hover:bg-[var(--color-primary)] hover:text-[var(--color-on-primary)]"
    >
      {label}
    </button>
  )
}
