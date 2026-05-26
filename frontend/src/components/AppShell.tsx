import type { ReactNode } from 'react'
import { MaterialIcon } from './MaterialIcon'

interface AppShellProps {
  sidebar: ReactNode
  chat: ReactNode
  source: ReactNode | null
  sidebarOpen: boolean
  sourceOpen: boolean
  showSidebarMobile?: boolean
  showSourceMobile?: boolean
  onOpenSidebar?: () => void
  onOpenSource?: () => void
}

/** Stitch dashboard: dinamik 3 sütun grid. */
export function AppShell({
  sidebar,
  chat,
  source,
  sidebarOpen,
  sourceOpen,
  showSidebarMobile = false,
  showSourceMobile = false,
  onOpenSidebar,
  onOpenSource,
}: AppShellProps) {
  const sidebarCol = sidebarOpen
    ? 'var(--sidebar-width)'
    : 'var(--sidebar-collapsed-width)'
  const sourceCol = sourceOpen && source ? 'var(--source-width)' : '0px'

  const layoutClass = [
    'dashboard-layout flex-1 min-h-0',
    showSidebarMobile ? 'show-sidebar' : '',
    showSourceMobile ? 'show-source' : '',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <div className="flex h-full flex-col overflow-hidden bg-white" data-testid="app-shell">
      <header className="flex items-center gap-3 border-b border-[var(--color-outline-variant)] px-4 py-3 lg:hidden">
        <button
          type="button"
          onClick={onOpenSidebar}
          className="flex items-center justify-center rounded-full bg-[var(--color-surface-container)] p-2"
          data-testid="open-sidebar"
          aria-label="Belgeler"
        >
          <MaterialIcon name="folder" className="text-[var(--color-on-surface-variant)]" />
        </button>
        <h1 className="flex-1 text-center text-sm font-semibold text-[var(--color-on-surface)]">
          Nexus RAG
        </h1>
        <button
          type="button"
          onClick={onOpenSource}
          className="flex items-center justify-center rounded-full bg-[var(--color-surface-container)] p-2"
          data-testid="open-source"
          aria-label="Kaynak"
        >
          <MaterialIcon name="menu_book" className="text-[var(--color-on-surface-variant)]" />
        </button>
      </header>
      <div
        className={layoutClass}
        style={{
          gridTemplateColumns: `${sidebarCol} 1fr ${sourceCol}`,
        }}
      >
        <div className="sidebar-left min-h-0 overflow-hidden">{sidebar}</div>
        <div className="chat-center min-h-0 overflow-hidden">{chat}</div>
        <div
          className={`drawer-right min-h-0 overflow-hidden ${sourceOpen && source ? 'drawer-right--spaced' : ''}`}
        >
          {source}
        </div>
      </div>
    </div>
  )
}
