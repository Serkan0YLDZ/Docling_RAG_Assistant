import { useCallback, useRef, useState, type ReactNode } from 'react'
import { MaterialIcon } from './MaterialIcon'

interface GlobalDropZoneProps {
  children: ReactNode
  onFiles: (files: FileList) => Promise<void>
}

/** Tüm ekranda sürükle-bırak ile dosya yükleme alanı sağlar. */
export function GlobalDropZone({ children, onFiles }: GlobalDropZoneProps) {
  const [dragging, setDragging] = useState(false)
  const dragDepth = useRef(0)
  const inputRef = useRef<HTMLInputElement>(null)

  const hasFiles = (e: React.DragEvent) =>
    Array.from(e.dataTransfer.types).includes('Files')

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (!hasFiles(e)) return
    dragDepth.current += 1
    setDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (!hasFiles(e)) return
    dragDepth.current -= 1
    if (dragDepth.current <= 0) {
      dragDepth.current = 0
      setDragging(false)
    }
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (hasFiles(e)) e.dataTransfer.dropEffect = 'copy'
  }, [])

  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault()
      e.stopPropagation()
      dragDepth.current = 0
      setDragging(false)
      const files = e.dataTransfer.files
      if (files?.length) await onFiles(files)
    },
    [onFiles],
  )

  const handleInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files?.length) await onFiles(files)
    e.target.value = ''
  }

  return (
    <div
      className="relative flex h-screen flex-col overflow-hidden"
      data-testid="global-drop-zone"
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={(e) => void handleDrop(e)}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
        multiple
        className="hidden"
        data-testid="file-input"
        onChange={(e) => void handleInputChange(e)}
      />

      {dragging && (
        <div
          className="pointer-events-none absolute inset-0 z-50 flex items-center justify-center bg-[var(--color-primary)]/10 backdrop-blur-[2px]"
          data-testid="drop-overlay"
        >
          <div className="flex flex-col items-center gap-3 rounded-2xl border-2 border-dashed border-[var(--color-primary)] bg-white/95 px-12 py-10 shadow-lg">
            <MaterialIcon name="upload_file" className="text-[var(--color-primary)]" size={40} />
            <p className="text-lg font-semibold text-[var(--color-on-surface)]">
              Dosyaları buraya bırakın
            </p>
            <p className="text-sm text-[var(--color-on-surface-variant)]">
              PDF, DOCX veya TXT
            </p>
          </div>
        </div>
      )}

      <div className="flex min-h-0 flex-1 flex-col">{children}</div>
    </div>
  )
}

/** Gizli dosya seçicisini açar (sohbet attach ikonu için). */
export function openGlobalFilePicker() {
  document.querySelector<HTMLInputElement>('[data-testid="file-input"]')?.click()
}
