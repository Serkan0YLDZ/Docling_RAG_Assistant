import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { SourcePanel } from './SourcePanel'

const sources = [
  {
    documentId: '1',
    documentName: 'Q3_Financial_Report.pdf',
    page: 12,
    highlightText:
      'Araştırma ve Geliştirme (Ar-Ge) departmanına ayrılan bütçe toplamın en büyük dilimini',
    mimeKind: 'pdf' as const,
    refIndex: 1,
  },
  {
    documentId: '2',
    documentName: 'ArGe_Yatirim_Ozeti.txt',
    page: 4,
    highlightText: "Ar-Ge maliyetlerinde %12'lik",
    mimeKind: 'text' as const,
    refIndex: 2,
  },
]

beforeEach(() => {
  vi.stubGlobal('requestAnimationFrame', (cb: FrameRequestCallback) => {
    cb(0)
    return 0
  })
  HTMLElement.prototype.scrollIntoView = vi.fn()
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('SourcePanel', () => {
  it('shows close button on desktop', () => {
    render(
      <SourcePanel
        sources={sources}
        activeRefIndex={1}
        onSelectSource={vi.fn()}
        onOpenDocument={vi.fn()}
        onClose={vi.fn()}
      />,
    )
    expect(screen.getByTestId('source-panel-close')).toBeInTheDocument()
    expect(screen.getByTestId('source-highlight')).toBeInTheDocument()
  })

  it('scrolls to active source when ref index changes', () => {
    const scrollIntoView = vi.mocked(HTMLElement.prototype.scrollIntoView)

    const { rerender } = render(
      <SourcePanel
        sources={sources}
        activeRefIndex={1}
        onSelectSource={vi.fn()}
        onOpenDocument={vi.fn()}
        onClose={vi.fn()}
      />,
    )
    scrollIntoView.mockClear()

    rerender(
      <SourcePanel
        sources={sources}
        activeRefIndex={2}
        onSelectSource={vi.fn()}
        onOpenDocument={vi.fn()}
        onClose={vi.fn()}
      />,
    )

    expect(scrollIntoView).toHaveBeenCalled()
    const highlight = screen.getByTestId('source-highlight')
    expect(highlight).toHaveAttribute('data-source-highlight')
  })

  it('calls onClose', async () => {
    const onClose = vi.fn()
    const user = userEvent.setup()
    render(
      <SourcePanel
        sources={sources}
        activeRefIndex={1}
        onSelectSource={vi.fn()}
        onOpenDocument={vi.fn()}
        onClose={onClose}
      />,
    )
    await user.click(screen.getByTestId('source-panel-close'))
    expect(onClose).toHaveBeenCalled()
  })

  it('calls onOpenDocument when belgede göster clicked', async () => {
    const onOpenDocument = vi.fn()
    const user = userEvent.setup()
    render(
      <SourcePanel
        sources={sources}
        activeRefIndex={1}
        onSelectSource={vi.fn()}
        onOpenDocument={onOpenDocument}
        onClose={vi.fn()}
      />,
    )
    await user.click(screen.getByTestId('source-open-doc-1'))
    expect(onOpenDocument).toHaveBeenCalledWith(sources[0])
  })
})
