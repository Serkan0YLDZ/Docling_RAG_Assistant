import { describe, expect, it } from 'vitest'
import { formatDocumentMeta } from './formatDocumentMeta'

describe('formatDocumentMeta', () => {
  it('shows chunk count when ready', () => {
    const text = formatDocumentMeta({
      id: '1',
      name: 'a.pdf',
      status: 'ready',
      progress: 100,
      uploadedAt: '',
      sizeLabel: '2.4 MB',
      mimeKind: 'pdf',
      chunkCount: 24,
    })
    expect(text).toBe('24 chunk • 2.4 MB')
  })

  it('shows indexing when processing', () => {
    const text = formatDocumentMeta({
      id: '1',
      name: 'a.pdf',
      status: 'processing',
      progress: 45,
      uploadedAt: '',
      sizeLabel: '2.4 MB',
      mimeKind: 'pdf',
      chunkCount: 0,
    })
    expect(text).toContain('İndeksleniyor')
  })
})
