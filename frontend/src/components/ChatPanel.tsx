import { useRef, useState } from 'react'
import type { ChatMessage, Citation } from '../api/types'
import { splitContentWithCitations } from '../utils/citationParser'
import { CitationChip } from './CitationChip'
import { MaterialIcon } from './MaterialIcon'

interface ChatPanelProps {
  messages: ChatMessage[]
  thinking: boolean
  onSend: (text: string) => Promise<void>
  onCitationClick: (citation: Citation) => void
  onAttach?: () => void
}

/** Orta panel: Stitch sohbet arayüzü. */
export function ChatPanel({
  messages,
  thinking,
  onSend,
  onCitationClick,
  onAttach,
}: ChatPanelProps) {
  const [input, setInput] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = async () => {
    const text = input.trim()
    if (!text || thinking || text.length < 10) return
    setInput('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
    await onSend(text)
  }

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      void handleSubmit()
    }
  }

  return (
    <main
      className="flex h-full flex-col overflow-hidden border-x border-[var(--color-outline-variant)] bg-white"
      data-testid="chat-panel"
    >
      <div className="flex flex-1 flex-col gap-10 overflow-y-auto px-8 py-8 md:px-12">
        {messages.map((msg) =>
          msg.role === 'user' ? (
            <div key={msg.id} className="flex flex-col items-end gap-2">
              <div className="max-w-[85%] rounded-2xl rounded-tr-sm border border-[var(--color-outline-variant)]/50 bg-[var(--color-surface-container)] px-6 py-4 text-[15px] leading-6 text-[var(--color-on-surface)] shadow-sm">
                {msg.content}
              </div>
            </div>
          ) : (
            <div key={msg.id} className="flex flex-col items-start gap-4">
              <AssistantContent
                content={msg.content}
                citations={msg.citations}
                onCitationClick={onCitationClick}
              />
            </div>
          ),
        )}
        {thinking && (
          <div className="flex items-center gap-2 text-sm text-[var(--color-on-surface-variant)]">
            <span
              className="h-2 w-2 animate-pulse rounded-full bg-[var(--color-primary)]"
              data-testid="thinking-dot"
            />
            Düşünüyor…
          </div>
        )}
      </div>

      <div className="bg-white p-6 md:p-8">
        <div className="relative flex items-end rounded-2xl border border-[var(--color-outline-variant)] bg-white p-4 shadow-sm transition-all hover:shadow-md focus-within:border-[var(--color-outline)] focus-within:ring-1 focus-within:ring-[var(--color-outline)]">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder="Bir soru sorun..."
            maxLength={500}
            rows={1}
            disabled={thinking}
            data-testid="chat-input"
            className="min-h-[56px] max-h-[200px] w-full resize-none border-none bg-transparent px-2 py-2 text-[15px] leading-relaxed text-[var(--color-on-surface)] placeholder:text-[var(--color-outline)] focus:ring-0"
          />
          <div className="mb-2 ml-4 flex items-center gap-2">
            <button
              type="button"
              onClick={onAttach ?? (() => textareaRef.current?.focus())}
              className="flex items-center justify-center rounded-full bg-[var(--color-surface-container)] p-2 text-[var(--color-on-surface-variant)] transition-colors hover:text-[var(--color-primary)]"
              aria-label="Dosya ekle"
            >
              <MaterialIcon name="attach_file" />
            </button>
            <button
              type="button"
              onClick={() => void handleSubmit()}
              disabled={thinking || input.trim().length < 10}
              data-testid="chat-send"
              className="flex items-center justify-center rounded-xl bg-[var(--color-primary)] p-2 text-white shadow-sm transition-colors hover:bg-[var(--color-primary)]/90 disabled:opacity-50"
              aria-label="Gönder"
            >
              <MaterialIcon name="arrow_upward" />
            </button>
          </div>
        </div>
      </div>
    </main>
  )
}

function AssistantContent({
  content,
  citations,
  onCitationClick,
}: {
  content: string
  citations?: Citation[]
  onCitationClick: (c: Citation) => void
}) {
  const paragraphs = content.split('\n\n').filter(Boolean)

  return (
    <div className="prose max-w-none w-full text-[15px] leading-loose text-[var(--color-on-surface)]">
      {paragraphs.map((para, pi) => (
        <p key={pi} className={pi > 0 ? 'mt-4' : ''}>
          <ParagraphWithCitations
            text={para}
            citations={citations}
            onCitationClick={onCitationClick}
          />
        </p>
      ))}
    </div>
  )
}

function ParagraphWithCitations({
  text,
  citations,
  onCitationClick,
}: {
  text: string
  citations?: Citation[]
  onCitationClick: (c: Citation) => void
}) {
  const parts = splitContentWithCitations(text)
  return (
    <>
      {parts.map((part, i) => {
        if (part.type === 'citation') {
          const ref = part.refIndex ?? 1
          const label = part.value.match(/Sayfa/i) ? part.value : `[${ref}]`
          const citation = citations?.find((c) => c.refIndex === ref)
          return (
            <CitationChip
              key={i}
              label={label}
              onClick={() => {
                if (citation) onCitationClick(citation)
              }}
            />
          )
        }
        const boldParts = part.value.split(/(\*\*[^*]+\*\*)/g)
        return (
          <span key={i}>
            {boldParts.map((bp, j) =>
              bp.startsWith('**') && bp.endsWith('**') ? (
                <strong key={j}>{bp.slice(2, -2)}</strong>
              ) : (
                <span key={j}>{bp}</span>
              ),
            )}
          </span>
        )
      })}
    </>
  )
}
