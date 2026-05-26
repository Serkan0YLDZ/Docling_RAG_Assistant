import { useCallback, useEffect, useState } from 'react'
import {
  deleteDocument,
  getMessages,
  listDocuments,
  listSources,
  resetChat,
  selectDocument,
  sendQuery,
  uploadDocument,
} from './api/client'
import type { ChatMessage, Citation, DocumentItem, SourcePreview } from './api/types'
import { AppShell } from './components/AppShell'
import { ChatPanel } from './components/ChatPanel'
import { DocumentSidebar } from './components/DocumentSidebar'
import { ErrorToast } from './components/ErrorToast'
import { GlobalDropZone, openGlobalFilePicker } from './components/GlobalDropZone'
import { SidebarCollapsedRail } from './components/SidebarCollapsedRail'
import {
  DocumentViewerModal,
  type DocumentViewerTarget,
} from './components/DocumentViewerModal'
import { SourcePanel } from './components/SourcePanel'

function App() {
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [checkedIds, setCheckedIds] = useState<Set<string>>(new Set())
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [sources, setSources] = useState<SourcePreview[]>([])
  const [activeRefIndex, setActiveRefIndex] = useState<number | null>(1)
  const [thinking, setThinking] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [sourcePanelOpen, setSourcePanelOpen] = useState(true)
  const [sidebarMobile, setSidebarMobile] = useState(false)
  const [sourceMobile, setSourceMobile] = useState(false)
  const [documentViewer, setDocumentViewer] = useState<DocumentViewerTarget | null>(
    null,
  )

  const syncSelection = useCallback((list: DocumentItem[], currentSelected: string | null) => {
    if (list.length === 0) {
      setSelectedId(null)
      setCheckedIds(new Set())
      selectDocument(null)
      return
    }
    const nextSelected = list.some((d) => d.id === currentSelected)
      ? currentSelected
      : list[0].id
    setSelectedId(nextSelected)
    selectDocument(nextSelected)
    setCheckedIds((prev) => {
      const next = new Set<string>()
      for (const id of prev) {
        if (list.some((d) => d.id === id)) next.add(id)
      }
      if (next.size === 0 && nextSelected) next.add(nextSelected)
      return next
    })
  }, [])

  const refreshDocuments = useCallback(async () => {
    const list = await listDocuments()
    setDocuments(list)
    syncSelection(list, selectedId)
  }, [selectedId, syncSelection])

  const refreshSources = useCallback(async () => {
    const list = await listSources()
    setSources(list)
    if (list.length === 0) {
      setSourcePanelOpen(false)
      return
    }
    if (activeRefIndex == null) {
      setActiveRefIndex(list[0].refIndex ?? 1)
    }
  }, [activeRefIndex])

  useEffect(() => {
    void refreshDocuments().catch((e: Error) => setError(e.message))
    void getMessages().then(setMessages).catch(() => setMessages([]))
    void refreshSources().catch(() => {
      setSources([])
      setSourcePanelOpen(false)
    })
  }, [refreshDocuments, refreshSources])

  useEffect(() => {
    const processing = documents.some((d) => d.status === 'processing')
    if (!processing) return
    const id = window.setInterval(() => void refreshDocuments(), 800)
    return () => clearInterval(id)
  }, [documents, refreshDocuments])

  const handleUploadFiles = async (files: FileList) => {
    try {
      setError(null)
      let lastId: string | null = null
      for (let i = 0; i < files.length; i++) {
        const doc = await uploadDocument(files[i])
        lastId = doc.id
      }
      const list = await listDocuments()
      setDocuments(list)
      if (lastId) {
        setSelectedId(lastId)
        selectDocument(lastId)
        setCheckedIds((prev) => new Set([...prev, lastId!]))
        setSidebarOpen(true)
      } else {
        syncSelection(list, selectedId)
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Yükleme hatası')
    }
  }

  const handleDelete = async (id: string) => {
    try {
      setError(null)
      await deleteDocument(id)
      const list = await listDocuments()
      setDocuments(list)
      const nextSelected = selectedId === id ? (list[0]?.id ?? null) : selectedId
      syncSelection(list, nextSelected)
      await refreshSources()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Silme hatası')
    }
  }

  const handleSend = async (text: string) => {
    try {
      setError(null)
      setThinking(true)
      const userMsg: ChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: text,
      }
      setMessages((prev) => [...prev, userMsg])
      const readyChecked = Array.from(checkedIds).filter((id) => {
        const doc = documents.find((d) => d.id === id)
        return doc?.status === 'ready' && (doc.chunkCount ?? 0) > 0
      })
      const scope =
        readyChecked.length > 0
          ? readyChecked
          : documents
              .filter((d) => d.status === 'ready' && (d.chunkCount ?? 0) > 0)
              .map((d) => d.id)
      const res = await sendQuery(text, scope.length ? scope : undefined)
      setMessages((prev) => [...prev, res.message])
      if (res.sources.length) {
        setSources(res.sources)
        setActiveRefIndex(res.sources[0].refIndex ?? 1)
        setSourcePanelOpen(true)
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Sorgu hatası')
    } finally {
      setThinking(false)
    }
  }

  const handleResetChat = async () => {
    try {
      setError(null)
      await resetChat()
      setMessages([])
      setSources([])
      setActiveRefIndex(null)
      setSourcePanelOpen(false)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Sohbet sıfırlanamadı')
    }
  }

  const handleCitation = (citation: Citation) => {
    setActiveRefIndex(citation.refIndex)
    setSourcePanelOpen(true)
    setSourceMobile(true)
  }

  const handleOpenDocument = (source: SourcePreview) => {
    setDocumentViewer({
      documentId: source.documentId,
      documentName: source.documentName,
      page: source.page ?? 1,
      mimeKind: source.mimeKind,
    })
  }

  const handleToggleCheck = (id: string) => {
    setCheckedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const sidebarContent = sidebarOpen ? (
    <DocumentSidebar
      documents={documents}
      selectedId={selectedId}
      checkedIds={checkedIds}
      onSelect={(id) => {
        setSelectedId(id)
        selectDocument(id)
        setSidebarMobile(false)
      }}
      onToggleCheck={handleToggleCheck}
      onDelete={(id) => void handleDelete(id)}
      onCollapse={() => setSidebarOpen(false)}
      onResetChat={() => void handleResetChat()}
      onUploadClick={openGlobalFilePicker}
    />
  ) : (
    <SidebarCollapsedRail onExpand={() => setSidebarOpen(true)} />
  )

  const sourceContent =
    sourcePanelOpen && sources.length > 0 ? (
      <SourcePanel
        sources={sources}
        activeRefIndex={activeRefIndex}
        onSelectSource={(ref) => {
          setActiveRefIndex(ref)
          setSourceMobile(true)
        }}
        onOpenDocument={handleOpenDocument}
        onClose={() => setSourcePanelOpen(false)}
      />
    ) : null

  return (
    <GlobalDropZone onFiles={handleUploadFiles}>
      <AppShell
        sidebarOpen={sidebarOpen}
        sourceOpen={sourcePanelOpen}
        showSidebarMobile={sidebarMobile}
        showSourceMobile={sourceMobile}
        onOpenSidebar={() => {
          setSidebarOpen(true)
          setSidebarMobile(true)
        }}
        onOpenSource={() => {
          setSourcePanelOpen(true)
          setSourceMobile(true)
        }}
        sidebar={sidebarContent}
        chat={
          <ChatPanel
            messages={messages}
            thinking={thinking}
            onSend={handleSend}
            onCitationClick={handleCitation}
            onAttach={openGlobalFilePicker}
          />
        }
        source={sourceContent}
      />
      <ErrorToast message={error} onDismiss={() => setError(null)} />
      <DocumentViewerModal
        target={documentViewer}
        onClose={() => setDocumentViewer(null)}
      />
    </GlobalDropZone>
  )
}

export default App
