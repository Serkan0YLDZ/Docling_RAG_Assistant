import { beforeEach, describe, expect, it } from 'vitest'
import {
  mockListDocuments,
  mockQuery,
  mockUploadDocument,
  resetMockStore,
} from './mockApi'

beforeEach(() => resetMockStore())

describe('mockApi', () => {
  it('rejects empty file', async () => {
    const file = new File([], 'empty.pdf', { type: 'application/pdf' })
    await expect(mockUploadDocument(file)).rejects.toThrow('Boş dosya yüklenemez')
  })

  it('rejects short query', async () => {
    await expect(mockQuery('kısa')).rejects.toThrow('En az 10 karakter')
  })

  it('uploads valid pdf', async () => {
    const file = new File(['x'], 'rapor.pdf', { type: 'application/pdf' })
    const doc = await mockUploadDocument(file)
    expect(doc.name).toBe('rapor.pdf')
    const list = await mockListDocuments()
    expect(list.some((d) => d.id === doc.id)).toBe(true)
  })
})
