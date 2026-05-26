import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { ChatPanel } from './ChatPanel'

describe('ChatPanel', () => {
  it('renders stitch-style user bubble and textarea', () => {
    render(
      <ChatPanel
        messages={[
          {
            id: '1',
            role: 'user',
            content: "Mevcut finansal raporlara göre Q3'teki en büyük harcama kalemi nedir?",
          },
        ]}
        thinking={false}
        onSend={vi.fn()}
        onCitationClick={vi.fn()}
      />,
    )
    expect(screen.getByTestId('chat-panel')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Bir soru sorun...')).toBeInTheDocument()
  })

  it('calls onSend with valid question', async () => {
    const onSend = vi.fn().mockResolvedValue(undefined)
    const user = userEvent.setup()
    render(
      <ChatPanel
        messages={[]}
        thinking={false}
        onSend={onSend}
        onCitationClick={vi.fn()}
      />,
    )
    await user.type(screen.getByTestId('chat-input'), 'Bu belge ne anlatıyor?')
    await user.click(screen.getByTestId('chat-send'))
    expect(onSend).toHaveBeenCalledWith('Bu belge ne anlatıyor?')
  })
})
