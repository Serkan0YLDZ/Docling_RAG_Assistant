import { useCallback, useEffect, useRef, useState } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import { fetchDocumentFile } from '../api/client'
import { getPageScrollTop, pickVisiblePage } from '../utils/pdfViewerScroll'
import { isPdfDocument } from '../utils/isPdfDocument'
import { MaterialIcon } from './MaterialIcon'

import 'react-pdf/dist/Page/AnnotationLayer.css'
import 'react-pdf/dist/Page/TextLayer.css'

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).href

const A4_HEIGHT_RATIO = 1.414

export interface DocumentViewerTarget {
  documentId: string
  documentName: string
  page: number
  mimeKind?: string
}

interface DocumentViewerModalProps {
  target: DocumentViewerTarget | null
  onClose: () => void
}

/** Tam ekran PDF görüntüleyici (ESC / X ile kapanır). */
export function DocumentViewerModal({ target, onClose }: DocumentViewerModalProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const scrollTargetRef = useRef(1)
  const renderedPagesRef = useRef<Set<number>>(new Set())
  const didInitialScrollRef = useRef(false)

  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [nonPdf, setNonPdf] = useState(false)
  const [pageWidth, setPageWidth] = useState(800)
  const [numPages, setNumPages] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)

  const revokeUrl = useCallback(() => {
    setPdfUrl((prev) => {
      if (prev) URL.revokeObjectURL(prev)
      return null
    })
  }, [])

  const scrollToPage = useCallback((page: number, behavior: ScrollBehavior = 'auto') => {
    const container = scrollRef.current
    if (!container) return false
    const pageEl = container.querySelector<HTMLElement>(`[data-page-number="${page}"]`)
    if (!pageEl) return false
    const top = getPageScrollTop(container, pageEl)
    container.scrollTo({ top: Math.max(0, top - 12), behavior })
    setCurrentPage(page)
    return true
  }, [])

  const tryInitialScroll = useCallback(() => {
    const want = scrollTargetRef.current
    const total = numPages
    if (total <= 0) return false
    if (!renderedPagesRef.current.has(want)) return false

    const allRendered = renderedPagesRef.current.size >= total
    if (didInitialScrollRef.current && !allRendered) return true

    if (scrollToPage(want)) {
      if (allRendered) didInitialScrollRef.current = true
      return true
    }
    return false
  }, [numPages, scrollToPage])

  const resetViewerState = useCallback(() => {
    renderedPagesRef.current = new Set()
    didInitialScrollRef.current = false
    setNumPages(0)
    setCurrentPage(1)
  }, [])

  useEffect(() => {
    if (!target) {
      revokeUrl()
      setError(null)
      setNonPdf(false)
      setLoading(false)
      resetViewerState()
      return
    }

    scrollTargetRef.current = Math.max(1, target.page ?? 1)
    setCurrentPage(scrollTargetRef.current)
    resetViewerState()
    setCurrentPage(scrollTargetRef.current)

    const isPdf = isPdfDocument(target.mimeKind, target.documentName)
    if (!isPdf) {
      setNonPdf(true)
      setLoading(false)
      setError(null)
      revokeUrl()
      return
    }

    setNonPdf(false)
    setLoading(true)
    setError(null)
    revokeUrl()

    let cancelled = false
    void fetchDocumentFile(target.documentId)
      .then((blob) => {
        if (cancelled) return
        const pdfBlob =
          blob.type === 'application/pdf'
            ? blob
            : new Blob([blob], { type: 'application/pdf' })
        setPdfUrl(URL.createObjectURL(pdfBlob))
      })
      .catch((e: Error) => {
        if (!cancelled) setError(e.message || 'Belge yüklenemedi')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [target, revokeUrl, resetViewerState])

  useEffect(() => {
    if (!target) return
    const prevOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = prevOverflow
    }
  }, [target])

  useEffect(() => {
    if (!target) return
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [target, onClose])

  useEffect(() => () => revokeUrl(), [revokeUrl])

  useEffect(() => {
    const el = scrollRef.current
    if (!el || !target) return

    const updateWidth = () => {
      setPageWidth(Math.min(Math.max(el.clientWidth - 32, 320), 1200))
    }
    updateWidth()
    if (typeof ResizeObserver === 'undefined') return
    const ro = new ResizeObserver(updateWidth)
    ro.observe(el)
    return () => ro.disconnect()
  }, [target])

  useEffect(() => {
    if (!target || !pdfUrl || numPages === 0) return

    if (tryInitialScroll()) return

    const timer = window.setInterval(() => {
      if (tryInitialScroll()) window.clearInterval(timer)
    }, 150)
    return () => window.clearInterval(timer)
  }, [target, pdfUrl, numPages, tryInitialScroll])

  useEffect(() => {
    const container = scrollRef.current
    if (!container || numPages === 0 || !pdfUrl) return

    const onScroll = () => {
      setCurrentPage(pickVisiblePage(container, numPages))
    }

    container.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
    return () => container.removeEventListener('scroll', onScroll)
  }, [numPages, pdfUrl])

  const handlePageRendered = useCallback(
    (pageNum: number) => {
      renderedPagesRef.current.add(pageNum)
      requestAnimationFrame(() => {
        tryInitialScroll()
      })
    },
    [tryInitialScroll],
  )

  const handleDocumentLoad = useCallback(
    ({ numPages: total }: { numPages: number }) => {
      setNumPages(total)
      const clamped = Math.min(Math.max(1, scrollTargetRef.current), total)
      scrollTargetRef.current = clamped
      if (!didInitialScrollRef.current) {
        setCurrentPage(clamped)
      }
    },
    [],
  )

  if (!target) return null

  const pagePlaceholderHeight = Math.round(pageWidth * A4_HEIGHT_RATIO)

  return (
    <div
      className="fixed inset-0 z-[200] flex flex-col bg-[#1a1a1a]"
      role="dialog"
      aria-modal="true"
      aria-label={`${target.documentName} önizleme`}
      data-testid="document-viewer-modal"
    >
      <header className="flex shrink-0 items-center justify-between gap-4 border-b border-white/10 bg-[#252525] px-4 py-3 text-white">
        <div className="min-w-0 flex-1">
          <p className="truncate text-[15px] font-medium">{target.documentName}</p>
          <p className="text-[13px] text-white/70" data-testid="document-viewer-page-indicator">
            Sayfa {currentPage}
            {numPages > 0 ? ` / ${numPages}` : ''}
          </p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-white transition-colors hover:bg-white/10"
          aria-label="Görüntüleyiciyi kapat"
          data-testid="document-viewer-close"
        >
          <MaterialIcon name="close" size={24} />
        </button>
      </header>

      <div
        ref={scrollRef}
        className="relative flex min-h-0 flex-1 flex-col overflow-y-auto bg-[#525252] py-4"
      >
        {loading && (
          <p className="flex flex-1 items-center justify-center text-white/80">
            Belge yükleniyor…
          </p>
        )}

        {nonPdf && (
          <div className="flex flex-1 flex-col items-center justify-center gap-4 px-6 text-center text-white/90">
            <MaterialIcon name="description" size={48} className="text-white/50" />
            <p className="max-w-md text-[15px] leading-relaxed">
              Tam ekran önizleme yalnızca PDF belgeleri için kullanılabilir. DOCX ve TXT
              dosyalarını indirip bilgisayarınızda açabilirsiniz.
            </p>
            <button
              type="button"
              className="rounded-xl bg-[var(--color-primary)] px-5 py-2.5 text-[14px] font-medium text-white"
              onClick={() => {
                void fetchDocumentFile(target.documentId)
                  .then((blob) => {
                    const url = URL.createObjectURL(blob)
                    const a = document.createElement('a')
                    a.href = url
                    a.download = target.documentName
                    a.click()
                    URL.revokeObjectURL(url)
                  })
                  .catch(() => setError('İndirme başarısız'))
              }}
            >
              Dosyayı indir
            </button>
          </div>
        )}

        {error && !loading && !nonPdf && (
          <p className="flex flex-1 items-center justify-center px-6 text-center text-red-300">
            {error}
          </p>
        )}

        {pdfUrl && !nonPdf && !loading && (
          <Document
            file={pdfUrl}
            onLoadSuccess={handleDocumentLoad}
            onLoadError={() => setError('PDF yüklenemedi')}
            loading={
              <p className="py-12 text-center text-white/80">PDF işleniyor…</p>
            }
            className="mx-auto flex w-full max-w-[1200px] flex-col items-center gap-4 px-4"
          >
            {numPages > 0 &&
              Array.from({ length: numPages }, (_, i) => i + 1).map((pageNum) => (
                <div
                  key={pageNum}
                  data-page-number={pageNum}
                  className="w-full shadow-lg"
                  style={{ minHeight: pagePlaceholderHeight }}
                >
                  <Page
                    pageNumber={pageNum}
                    width={pageWidth}
                    renderTextLayer
                    renderAnnotationLayer
                    onRenderSuccess={() => handlePageRendered(pageNum)}
                  />
                </div>
              ))}
          </Document>
        )}
      </div>
    </div>
  )
}
