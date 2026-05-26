import { PanelToggleButton } from './PanelToggleButton'

interface SidebarCollapsedRailProps {
  onExpand: () => void
}

/** Sol panel kapalıyken ince şerit; tek genişlet düğmesi. */
export function SidebarCollapsedRail({ onExpand }: SidebarCollapsedRailProps) {
  return (
    <aside
      className="flex h-full w-full min-w-0 flex-col items-center bg-white pt-5"
      data-testid="sidebar-collapsed-rail"
    >
      <PanelToggleButton
        icon="chevron_right"
        label="Belge panelini aç"
        testId="sidebar-expand"
        onClick={onExpand}
      />
    </aside>
  )
}
