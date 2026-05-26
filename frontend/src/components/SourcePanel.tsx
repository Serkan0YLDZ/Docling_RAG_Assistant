import { useEffect, useRef, type KeyboardEvent } from 'react'
import type { SourcePreview } from '../api/types'
import { PanelToggleButton } from './PanelToggleButton'
import { MaterialIcon } from './MaterialIcon'

interface SourcePanelProps {
  sources: SourcePreview[]
  activeRefIndex: number | null
  onSelectSource: (refIndex: number) => void
  onOpenDocument: (source: SourcePreview) => void
  onClose: () => void
}

/** Sağ panel: Kaynak Önizleme kartları (Stitch). */
export function SourcePanel({
  sources,
  activeRefIndex,
  onSelectSource,
  onOpenDocument,
  onClose,
}: SourcePanelProps) {
  const listRef = useRef<HTMLDivElement>(null)
  const cardRefs = useRef<Map<number, HTMLElement>>(new Map())

  useEffect(() => {
    if (activeRefIndex == null) return
    const frame = requestAnimationFrame(() => {
      const card = cardRefs.current.get(activeRefIndex)
      card?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    })
    return () => cancelAnimationFrame(frame)
  }, [activeRefIndex, sources])

  const setCardRef = (refIndex: number) => (el: HTMLElement | null) => {
    if (el) cardRefs.current.set(refIndex, el)
    else cardRefs.current.delete(refIndex)
  }

  return (
    <aside
      className="flex h-full w-full min-w-0 flex-col overflow-hidden bg-white"
      data-testid="source-panel"
    >
      <div className="flex shrink-0 items-center justify-between gap-2 border-b border-[var(--color-outline-variant)] px-6 py-5">
        <div className="flex min-w-0 flex-col gap-1">
          <h2 className="text-lg font-semibold text-[var(--color-on-surface)]">
            Kaynak Önizleme
          </h2>
          <p className="text-[13px] text-[var(--color-on-surface-variant)]">
            Referans Detayları
          </p>
        </div>
        <PanelToggleButton
          icon="close"
          label="Kaynak panelini kapat"
          testId="source-panel-close"
          onClick={onClose}
        />
      </div>

      <div
        ref={listRef}
        className="flex flex-1 flex-col gap-6 overflow-y-auto px-8 pb-8 scroll-smooth"
        data-testid="source-panel-list"
      >
        {sources.map((source, index) => {
          const ref = source.refIndex ?? index + 1
          const isActive = activeRefIndex === ref
          const isPdf = source.mimeKind === 'pdf' || source.documentName.endsWith('.pdf')

          const selectCard = () => onSelectSource(ref)
          const onCardKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault()
              selectCard()
            }
          }

          return (
            <article
              key={`${source.documentId}-${ref}`}
              ref={setCardRef(ref)}
              className={`w-full scroll-mt-4 rounded-2xl border border-[var(--color-outline-variant)] bg-white p-6 text-left transition-all hover:shadow-md ${
                isActive ? 'shadow-md ring-1 ring-[var(--color-primary)]/20' : 'opacity-70 hover:opacity-100'
              }`}
              data-testid={`source-card-${ref}`}
              id={`source-ref-${ref}`}
            >
              <div
                role="button"
                tabIndex={0}
                onClick={selectCard}
                onKeyDown={onCardKeyDown}
                className="cursor-pointer text-left outline-none focus-visible:rounded-lg focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]"
              >
              <div className="mb-4 flex items-center gap-4 border-b border-[var(--color-outline-variant)]/50 pb-4">
                <div
                  className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${
                    isPdf ? 'bg-red-500/10 text-[var(--color-error)]' : 'bg-[var(--color-secondary)]/10 text-[var(--color-secondary)]'
                  }`}
                >
                  <MaterialIcon
                    name={isPdf ? 'picture_as_pdf' : 'description'}
                    size={18}
                  />
                </div>
                <h3 className="truncate text-[15px] font-medium text-[var(--color-on-surface)]">
                  {source.documentName}
                </h3>
              </div>
              <p
                className={`rounded-xl border border-[var(--color-outline-variant)]/30 bg-[var(--color-surface-container-low)] p-4 text-[13px] leading-relaxed text-[var(--color-on-surface-variant)] ${
                  isActive ? 'text-[var(--color-on-surface)]' : ''
                }`}
              >
                <mark
                  className={`rounded-md border border-[var(--color-citation-border)] bg-[var(--color-highlight)] px-1 py-0.5 font-medium text-[var(--color-on-surface)] ${
                    isActive ? '' : 'opacity-90'
                  }`}
                  data-source-highlight={isActive ? '' : undefined}
                  data-testid={isActive ? 'source-highlight' : undefined}
                >
                  {source.highlightText}
                </mark>
              </p>
              </div>
              <div className="mt-4 flex flex-wrap items-center gap-2 pt-2">
                <span className="rounded-md bg-[var(--color-surface-container)] px-2 py-1 text-[13px] font-medium text-[var(--color-on-surface)]">
                  Sayfa {source.page}
                </span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    onOpenDocument(source)
                  }}
                  className="flex h-8 items-center gap-1 rounded-lg border border-[var(--color-outline-variant)] bg-white px-2.5 text-[12px] font-medium text-[var(--color-primary)] transition-colors hover:bg-[var(--color-primary)]/5"
                  aria-label={`${source.documentName} belgesini sayfa ${source.page} ile aç`}
                  title={
                    isPdf
                      ? 'Belgeyi bu sayfadan aç'
                      : 'Belgeyi aç (sayfa bilgisi yalnızca PDF için geçerlidir)'
                  }
                  data-testid={`source-open-doc-${ref}`}
                >
                  <MaterialIcon name="open_in_new" size={16} />
                  Belgede göster
                </button>
                {source.section ? (
                  <span className="truncate text-[12px] text-[var(--color-on-surface-variant)]">
                    {source.section}
                  </span>
                ) : null}
              </div>
            </article>
          )
        })}
      </div>
    </aside>
  )
}
