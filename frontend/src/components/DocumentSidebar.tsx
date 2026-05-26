import type { DocumentItem } from '../api/types'
import { formatDocumentMeta } from '../utils/formatDocumentMeta'
import { MaterialIcon } from './MaterialIcon'
import { PanelToggleButton } from './PanelToggleButton'

interface DocumentSidebarProps {
  documents: DocumentItem[]
  selectedId: string | null
  checkedIds: Set<string>
  onSelect: (id: string) => void
  onToggleCheck: (id: string) => void
  onDelete: (id: string) => void
  onCollapse: () => void
  onResetChat: () => void
  onUploadClick: () => void
}

/** Sol panel: SON YÜKLENENLER listesi (Stitch). */
export function DocumentSidebar({
  documents,
  selectedId,
  checkedIds,
  onSelect,
  onToggleCheck,
  onDelete,
  onCollapse,
  onResetChat,
  onUploadClick,
}: DocumentSidebarProps) {
  return (
    <aside
      className="flex h-full w-full min-w-0 flex-col overflow-hidden bg-white"
      data-testid="document-sidebar"
    >
      <div className="flex shrink-0 items-center justify-between gap-2 border-b border-[var(--color-outline-variant)] px-4 py-4">
        <div className="flex min-w-0 flex-1 items-center gap-1">
          <h3 className="min-w-0 truncate text-[13px] font-semibold uppercase tracking-widest text-[var(--color-on-surface-variant)]">
            Son Yüklenenler
          </h3>
          <button
            type="button"
            onClick={onUploadClick}
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-[var(--color-primary)] transition-colors hover:bg-[var(--color-primary)]/10"
            aria-label="Belge yükle"
            data-testid="sidebar-upload"
          >
            <MaterialIcon name="upload_file" size={20} />
          </button>
        </div>
        <PanelToggleButton
          icon="chevron_left"
          label="Belge panelini küçült"
          testId="sidebar-collapse"
          onClick={onCollapse}
        />
      </div>

      <div className="flex flex-1 flex-col gap-4 overflow-y-auto px-4 pb-4">
        {documents.length === 0 && (
          <p className="text-sm leading-relaxed text-[var(--color-on-surface-variant)]">
            Belge eklemek için dosyayı ekranın herhangi bir yerine sürükleyip bırakın.
          </p>
        )}
        <div className="flex flex-col gap-2">
          {documents.map((doc) => {
            const isActive = selectedId === doc.id
            const isChecked = checkedIds.has(doc.id)
            return (
              <div
                key={doc.id}
                className={`group flex min-w-0 items-center gap-2 rounded-xl p-2 transition-colors hover:bg-[var(--color-surface-container)] ${
                  isActive ? 'bg-[var(--color-surface-container)]' : ''
                }`}
                data-testid={`doc-row-${doc.id}`}
              >
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={() => onToggleCheck(doc.id)}
                  onClick={(e) => e.stopPropagation()}
                  className="h-4 w-4 shrink-0 rounded border-[var(--color-outline-variant)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
                />
                <button
                  type="button"
                  onClick={() => onSelect(doc.id)}
                  className="flex min-w-0 flex-1 cursor-pointer items-center gap-2 overflow-hidden text-left"
                >
                  <MaterialIcon
                    name="description"
                    className="shrink-0 text-[var(--color-outline)]"
                    size={20}
                  />
                  <div className="min-w-0 flex-1 overflow-hidden">
                    <p
                      className="truncate text-[15px] font-medium leading-6 text-[var(--color-on-surface)]"
                      title={doc.name}
                    >
                      {doc.name}
                    </p>
                    <p
                      className={`mt-0.5 truncate text-[13px] leading-[18px] text-[var(--color-on-surface-variant)] ${
                        isActive ? 'font-medium text-[var(--color-primary)]' : ''
                      }`}
                    >
                      {formatDocumentMeta(doc)}
                    </p>
                  </div>
                </button>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    onDelete(doc.id)
                  }}
                  className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-[var(--color-on-surface)] opacity-0 transition-all group-hover:opacity-100 hover:bg-[var(--color-error)]/10 hover:text-[var(--color-error)] focus-visible:opacity-100"
                  aria-label={`${doc.name} dosyasını kaldır`}
                  data-testid={`doc-delete-${doc.id}`}
                >
                  <MaterialIcon name="close" size={18} weight={500} />
                </button>
              </div>
            )
          })}
        </div>
      </div>

      <div className="shrink-0 border-t border-[var(--color-outline-variant)] p-4">
        <button
          type="button"
          onClick={onResetChat}
          className="flex w-full items-center justify-center gap-2 rounded-xl border border-[var(--color-outline-variant)] bg-[var(--color-surface-container-low)] px-4 py-3 text-[14px] font-medium text-[var(--color-on-surface)] transition-colors hover:bg-[var(--color-surface-container)]"
          data-testid="chat-reset"
        >
          <MaterialIcon name="restart_alt" size={20} />
          Sohbeti Sıfırla
        </button>
      </div>
    </aside>
  )
}
