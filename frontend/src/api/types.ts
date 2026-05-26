export type DocumentStatus = 'queued' | 'processing' | 'ready' | 'error'

export interface DocumentItem {
  id: string
  name: string
  status: DocumentStatus
  progress: number
  uploadedAt: string
  sizeLabel: string
  mimeKind: 'pdf' | 'text' | 'doc'
  chunkCount: number
}

export interface Citation {
  refIndex: number
  page: number
  section?: string
  excerpt: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
}

export interface SourcePreview {
  documentId: string
  documentName: string
  page: number
  section?: string
  highlightText: string
  mimeKind?: 'pdf' | 'text'
  refIndex?: number
}

export interface QueryResponse {
  message: ChatMessage
  sources: SourcePreview[]
}
