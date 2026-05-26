import { render, screen, fireEvent } from '@testing-library/react'
import { describe, expect, it, vi, beforeEach } from 'vitest'
import { DocumentViewerModal } from './DocumentViewerModal'

vi.mock('react-pdf', () => ({
  pdfjs: { GlobalWorkerOptions: { workerSrc: '' } },
  Document: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="pdf-document">{children}</div>
  ),
  Page: ({
    pageNumber,
    onRenderSuccess,
  }: {
    pageNumber: number
    onRenderSuccess?: () => void
  }) => (
    <div
      data-testid={`pdf-page-${pageNumber}`}
      data-page-number={String(pageNumber)}
      ref={(el) => {
        if (el && onRenderSuccess) onRenderSuccess()
      }}
    >
      page {pageNumber}
    </div>
  ),
}))

vi.mock('../api/client', () => ({
  fetchDocumentFile: vi.fn(),
}))

import { fetchDocumentFile } from '../api/client'

describe('DocumentViewerModal', () => {
  beforeEach(() => {
    vi.mocked(fetchDocumentFile).mockReset()
  })

  it('renders nothing when target is null', () => {
    const { container } = render(<DocumentViewerModal target={null} onClose={vi.fn()} />)
    expect(container.firstChild).toBeNull()
  })

  it('closes on X button and Escape', () => {
    vi.mocked(fetchDocumentFile).mockResolvedValue(
      new Blob(['%PDF'], { type: 'application/pdf' }),
    )
    const onClose = vi.fn()
    render(
      <DocumentViewerModal
        target={{
          documentId: '1',
          documentName: 'rapor.pdf',
          page: 3,
          mimeKind: 'pdf',
        }}
        onClose={onClose}
      />,
    )
    fireEvent.click(screen.getByTestId('document-viewer-close'))
    expect(onClose).toHaveBeenCalled()

    fireEvent.keyDown(window, { key: 'Escape' })
    expect(onClose).toHaveBeenCalledTimes(2)
  })

  it('shows non-PDF message for docx', () => {
    render(
      <DocumentViewerModal
        target={{
          documentId: '1',
          documentName: 'rapor.docx',
          page: 1,
          mimeKind: 'doc',
        }}
        onClose={vi.fn()}
      />,
    )
    expect(screen.getByText(/yalnızca PDF/i)).toBeInTheDocument()
    expect(fetchDocumentFile).not.toHaveBeenCalled()
  })
})
