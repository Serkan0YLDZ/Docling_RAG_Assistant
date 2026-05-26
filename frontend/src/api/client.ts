import type {
  ChatMessage,
  DocumentItem,
  QueryResponse,
  SourcePreview,
} from './types'
import {
  mockGetMessages,
  mockGetSourcePreview,
  mockDeleteDocument,
  mockListDocuments,
  mockListSources,
  mockQuery,
  mockResetChat,
  mockSelectDocument,
  mockUploadDocument,
} from './mockApi'

const useMock = import.meta.env.VITE_USE_MOCK !== 'false'
const apiBase = import.meta.env.VITE_API_URL ?? 'http://localhost:5000'

/** Mock modunun aktif olup olmadığını döner. */
export function isMockMode(): boolean {
  return useMock
}

/** Tüm belgeleri listeler. */
export async function listDocuments(): Promise<DocumentItem[]> {
  if (useMock) return mockListDocuments()
  const res = await fetch(`${apiBase}/api/documents`)
  if (!res.ok) throw new Error('Belgeler yüklenemedi')
  return res.json()
}

/** Kaynak önizleme kartlarını listeler. */
export async function listSources(): Promise<SourcePreview[]> {
  if (useMock) return mockListSources()
  const res = await fetch(`${apiBase}/api/sources`)
  if (!res.ok) throw new Error('Kaynaklar yüklenemedi')
  return res.json()
}

/** Belge yükler. */
export async function uploadDocument(file: File): Promise<DocumentItem> {
  if (useMock) return mockUploadDocument(file)
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${apiBase}/api/documents`, { method: 'POST', body: form })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.error ?? 'Yükleme başarısız')
  return data
}

/** Belgeyi siler. */
export async function deleteDocument(id: string): Promise<void> {
  if (useMock) return mockDeleteDocument(id)
  const res = await fetch(`${apiBase}/api/documents/${id}`, { method: 'DELETE' })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.error ?? 'Belge silinemedi')
  }
}

/** Aktif belgeyi seçer. */
export function selectDocument(id: string | null) {
  if (useMock) mockSelectDocument(id)
}

/** Sohbet mesajlarını getirir. */
export async function getMessages(): Promise<ChatMessage[]> {
  if (useMock) return mockGetMessages()
  const res = await fetch(`${apiBase}/api/chat/messages`)
  if (!res.ok) throw new Error('Mesajlar alınamadı')
  return res.json()
}

/** Sohbet geçmişini ve son kaynakları sıfırlar. */
export async function resetChat(): Promise<void> {
  if (useMock) return mockResetChat()
  const res = await fetch(`${apiBase}/api/chat/reset`, { method: 'POST' })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.error ?? 'Sohbet sıfırlanamadı')
  }
}

/** Soru gönderir ve yanıt alır. */
export async function sendQuery(
  question: string,
  documentIds?: string[],
): Promise<QueryResponse> {
  if (useMock) return mockQuery(question)
  const res = await fetch(`${apiBase}/api/chat/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: question,
      ...(documentIds?.length ? { documentIds } : {}),
    }),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.error ?? 'Sorgu başarısız')
  return data
}

/** Orijinal belge dosyasının URL'sini döner. */
export function getDocumentFileUrl(documentId: string): string {
  return `${apiBase}/api/documents/${documentId}/file`
}

/** Orijinal belge dosyasını blob olarak indirir (görüntüleyici için). */
export async function fetchDocumentFile(documentId: string): Promise<Blob> {
  const res = await fetch(getDocumentFileUrl(documentId))
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error((data as { error?: string }).error ?? 'Belge yüklenemedi')
  }
  return res.blob()
}

/** Kaynak önizlemesi getirir (refIndex veya sayfa). */
export async function getSourcePreview(
  documentId: string,
  refOrPage: number,
): Promise<SourcePreview> {
  if (useMock) return mockGetSourcePreview(documentId, refOrPage)
  const res = await fetch(
    `${apiBase}/api/documents/${documentId}/source?ref=${refOrPage}`,
  )
  if (!res.ok) throw new Error('Kaynak yüklenemedi')
  return res.json()
}
