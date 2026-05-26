import { describe, expect, it } from 'vitest'
import type { DocumentItem } from './types'

describe('API types', () => {
  it('DocumentItem has chunkCount', () => {
    const doc: DocumentItem = {
      id: '1',
      name: 'Q3_Financial_Report.pdf',
      status: 'ready',
      progress: 100,
      uploadedAt: new Date().toISOString(),
      sizeLabel: '2.4 MB',
      mimeKind: 'pdf',
      chunkCount: 24,
    }
    expect(doc.chunkCount).toBe(24)
  })
})
