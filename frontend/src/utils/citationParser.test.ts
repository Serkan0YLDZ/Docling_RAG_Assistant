import { describe, expect, it } from 'vitest'
import { parseCitationRefs, splitContentWithCitations } from './citationParser'

describe('citationParser', () => {
  it('parses numeric ref [1]', () => {
    const refs = parseCitationRefs('Metin [1] devam')
    expect(refs[0].refIndex).toBe(1)
  })

  it('splits content with [2] chips', () => {
    const parts = splitContentWithCitations('Özet [2] son.')
    expect(parts.some((p) => p.type === 'citation' && p.refIndex === 2)).toBe(true)
  })
})
