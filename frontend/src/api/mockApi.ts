import type {
  ChatMessage,
  DocumentItem,
  QueryResponse,
  SourcePreview,
} from './types'
import { formatFileSize } from '../utils/formatFileSize'

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms))

export const MOCK_SOURCES: SourcePreview[] = [
  {
    documentId: 'doc-1',
    documentName: 'Q3_Financial_Report.pdf',
    page: 12,
    highlightText:
      'Araştırma ve Geliştirme (Ar-Ge) departmanına ayrılan bütçe toplamın en büyük dilimini',
    mimeKind: 'pdf',
    refIndex: 1,
  },
  {
    documentId: 'doc-2',
    documentName: 'ArGe_Yatirim_Ozeti.txt',
    page: 4,
    highlightText: 'Ar-Ge maliyetlerinde %12',
    mimeKind: 'text',
    refIndex: 2,
  },
]

let documents: DocumentItem[] = [
  {
    id: 'doc-1',
    name: 'Q3_Financial_Report.pdf',
    status: 'ready',
    progress: 100,
    uploadedAt: new Date(Date.now() - 86400000).toISOString(),
    sizeLabel: '2.4 MB',
    mimeKind: 'pdf',
    chunkCount: 24,
  },
  {
    id: 'doc-2',
    name: 'API_Documentation_v2.txt',
    status: 'ready',
    progress: 100,
    uploadedAt: new Date(Date.now() - 172800000).toISOString(),
    sizeLabel: '45 KB',
    mimeKind: 'text',
    chunkCount: 8,
  },
]

function estimateChunkCount(fileSize: number): number {
  return Math.max(4, Math.min(64, Math.round(fileSize / 40_000)))
}

let messages: ChatMessage[] = [
  {
    id: 'msg-u1',
    role: 'user',
    content:
      "Mevcut finansal raporlara göre Q3'teki en büyük harcama kalemi nedir?",
  },
  {
    id: 'msg-a1',
    role: 'assistant',
    content:
      "Analiz edilen belgelere göre, 2023 Q3 dönemindeki en büyük harcama kalemi **Araştırma ve Geliştirme (Ar-Ge)** faaliyetleridir. [1]\n\nAr-Ge harcamaları toplam bütçenin %34'ünü oluşturmuş olup, bir önceki çeyreğe göre %12 artış göstermiştir. [2]",
    citations: [
      {
        refIndex: 1,
        page: 12,
        excerpt: MOCK_SOURCES[0].highlightText,
      },
      {
        refIndex: 2,
        page: 4,
        excerpt: MOCK_SOURCES[1].highlightText,
      },
    ],
  },
]

let selectedDocumentId: string | null = 'doc-1'

/** Mock belge listesini döner. */
export async function mockListDocuments(): Promise<DocumentItem[]> {
  await delay(200)
  return [...documents]
}

/** Mock kaynak kartlarını döner. */
export async function mockListSources(): Promise<SourcePreview[]> {
  await delay(100)
  const docIds = new Set(documents.map((d) => d.id))
  return MOCK_SOURCES.filter((s) => docIds.has(s.documentId))
}

/** Mock belgeyi listeden siler. */
export async function mockDeleteDocument(id: string): Promise<void> {
  await delay(150)
  documents = documents.filter((d) => d.id !== id)
  if (selectedDocumentId === id) {
    selectedDocumentId = documents[0]?.id ?? null
  }
}

/** Mock dosya yükler ve işleme simülasyonu başlatır. */
export async function mockUploadDocument(file: File): Promise<DocumentItem> {
  if (file.size === 0) {
    throw new Error('Boş dosya yüklenemez')
  }
  const maxBytes = 50 * 1024 * 1024
  if (file.size > maxBytes) {
    throw new Error('Maksimum dosya boyutu aşıldı (50 MB)')
  }
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (ext !== 'pdf' && ext !== 'docx' && ext !== 'txt') {
    throw new Error('Yalnızca PDF, DOCX veya TXT dosyaları kabul edilir')
  }

  const doc: DocumentItem = {
    id: `doc-${Date.now()}`,
    name: file.name,
    status: 'queued',
    progress: 0,
    uploadedAt: new Date().toISOString(),
    sizeLabel: formatFileSize(file.size),
    mimeKind: ext === 'pdf' ? 'pdf' : ext === 'txt' ? 'text' : 'doc',
    chunkCount: 0,
  }
  documents = [doc, ...documents]
  selectedDocumentId = doc.id
  simulateProcessing(doc.id, file.size)
  return doc
}

async function simulateProcessing(docId: string, fileSize: number) {
  await delay(400)
  updateDoc(docId, { status: 'processing', progress: 20, chunkCount: 0 })
  await delay(600)
  updateDoc(docId, { progress: 55, chunkCount: Math.floor(estimateChunkCount(fileSize) * 0.4) })
  await delay(600)
  updateDoc(docId, { progress: 85, chunkCount: Math.floor(estimateChunkCount(fileSize) * 0.8) })
  await delay(500)
  updateDoc(docId, {
    status: 'ready',
    progress: 100,
    chunkCount: estimateChunkCount(fileSize),
  })
}

function updateDoc(id: string, patch: Partial<DocumentItem>) {
  documents = documents.map((d) => (d.id === id ? { ...d, ...patch } : d))
}

/** Seçili belge kimliğini ayarlar. */
export function mockSelectDocument(id: string | null) {
  selectedDocumentId = id
}

/** Mock sohbet geçmişini döner. */
export async function mockGetMessages(): Promise<ChatMessage[]> {
  await delay(100)
  return [...messages]
}

/** Mock soru-cevap üretir. */
export async function mockQuery(question: string): Promise<QueryResponse> {
  if (question.length < 10) {
    throw new Error('Lütfen daha açıklayıcı bir soru giriniz (En az 10 karakter)')
  }
  if (question.length > 500) {
    throw new Error('Karakter sınırı aşıldı, lütfen sorunuzu kısaltınız')
  }

  await delay(1200)

  const noContext = question.toLowerCase().includes('bilinmeyen')
  if (noContext) {
    const assistant: ChatMessage = {
      id: `msg-${Date.now()}-a`,
      role: 'assistant',
      content: 'Bu konuda bilgi bulunamadı',
    }
    messages = [...messages, assistant]
    return { message: assistant, sources: [] }
  }

  const doc = documents.find((d) => d.id === selectedDocumentId) ?? documents[0]
  const assistant: ChatMessage = {
    id: `msg-${Date.now()}-a`,
    role: 'assistant',
    content:
      'Belgelerinize göre en büyük harcama kalemi Ar-Ge yatırımlarıdır. [1] Detaylar finansal raporda özetlenmiştir. [2]',
    citations: MOCK_SOURCES.map((s, i) => ({
      refIndex: i + 1,
      page: s.page,
      excerpt: s.highlightText,
    })),
  }
  messages = [
    ...messages,
    { id: `msg-${Date.now()}-u`, role: 'user', content: question },
    assistant,
  ]

  const sources = MOCK_SOURCES.map((s) =>
    s.documentId === doc?.id || !doc
      ? s
      : { ...s, documentName: doc.name, documentId: doc.id },
  )

  return { message: assistant, sources }
}

/** Mock kaynak önizlemesi döner. */
export async function mockGetSourcePreview(
  documentId: string,
  refIndex: number,
): Promise<SourcePreview> {
  await delay(150)
  const found =
    MOCK_SOURCES.find((s) => s.refIndex === refIndex && s.documentId === documentId) ??
    MOCK_SOURCES.find((s) => s.refIndex === refIndex) ??
    MOCK_SOURCES[0]
  return { ...found }
}

/** Mock sohbet ve kaynakları sıfırlar. */
export async function mockResetChat(): Promise<void> {
  await delay(80)
  messages = []
}

/** Mock store'u test için sıfırlar. */
export function resetMockStore() {
  documents = []
  messages = []
  selectedDocumentId = null
}

