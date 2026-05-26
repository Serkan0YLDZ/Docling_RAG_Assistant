import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { DocumentSidebar } from './DocumentSidebar'

const docs = [
  {
    id: '1',
    name: 'Q3_Financial_Report.pdf',
    status: 'ready' as const,
    progress: 100,
    uploadedAt: new Date().toISOString(),
    sizeLabel: '2.4 MB',
    mimeKind: 'pdf' as const,
    chunkCount: 24,
  },
]

describe('DocumentSidebar', () => {
  it('shows chunk count instead of aktif/pasif', () => {
    render(
      <DocumentSidebar
        documents={docs}
        selectedId="1"
        checkedIds={new Set(['1'])}
        onSelect={vi.fn()}
        onToggleCheck={vi.fn()}
        onDelete={vi.fn()}
        onCollapse={vi.fn()}
        onResetChat={vi.fn()}
        onUploadClick={vi.fn()}
      />,
    )
    expect(screen.getByText(/24 chunk/)).toBeInTheDocument()
    expect(screen.queryByText(/Aktif/)).not.toBeInTheDocument()
    expect(screen.queryByText(/Pasif/)).not.toBeInTheDocument()
  })

  it('calls onCollapse', async () => {
    const onCollapse = vi.fn()
    const user = userEvent.setup()
    render(
      <DocumentSidebar
        documents={docs}
        selectedId="1"
        checkedIds={new Set(['1'])}
        onSelect={vi.fn()}
        onToggleCheck={vi.fn()}
        onDelete={vi.fn()}
        onCollapse={onCollapse}
        onResetChat={vi.fn()}
        onUploadClick={vi.fn()}
      />,
    )
    await user.click(screen.getByTestId('sidebar-collapse'))
    expect(onCollapse).toHaveBeenCalled()
  })

  it('calls onResetChat when reset button clicked', async () => {
    const onResetChat = vi.fn()
    const user = userEvent.setup()
    render(
      <DocumentSidebar
        documents={docs}
        selectedId="1"
        checkedIds={new Set(['1'])}
        onSelect={vi.fn()}
        onToggleCheck={vi.fn()}
        onDelete={vi.fn()}
        onCollapse={vi.fn()}
        onResetChat={onResetChat}
        onUploadClick={vi.fn()}
      />,
    )
    await user.click(screen.getByTestId('chat-reset'))
    expect(onResetChat).toHaveBeenCalled()
  })

  it('calls onUploadClick when upload icon clicked', async () => {
    const onUploadClick = vi.fn()
    const user = userEvent.setup()
    render(
      <DocumentSidebar
        documents={docs}
        selectedId="1"
        checkedIds={new Set(['1'])}
        onSelect={vi.fn()}
        onToggleCheck={vi.fn()}
        onDelete={vi.fn()}
        onCollapse={vi.fn()}
        onResetChat={vi.fn()}
        onUploadClick={onUploadClick}
      />,
    )
    await user.click(screen.getByTestId('sidebar-upload'))
    expect(onUploadClick).toHaveBeenCalled()
  })
})
