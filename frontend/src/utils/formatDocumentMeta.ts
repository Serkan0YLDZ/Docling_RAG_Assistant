import type { DocumentItem } from '../api/types'

/** Belge alt satırı: chunk sayısı veya indeksleme durumu. */
export function formatDocumentMeta(doc: DocumentItem): string {
  if (doc.status === 'processing') {
    return `İndeksleniyor • %${doc.progress}`
  }
  if (doc.status === 'queued') {
    return 'Kuyrukta'
  }
  if (doc.status === 'error') {
    return 'Hata'
  }
  if (doc.status === 'ready' && doc.chunkCount > 0) {
    return `${doc.chunkCount} chunk • ${doc.sizeLabel}`
  }
  return doc.sizeLabel
}
