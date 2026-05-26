/** Kaynak veya belge kaydının PDF olup olmadığını kontrol eder. */
export function isPdfDocument(mimeKind: string | undefined, fileName: string): boolean {
  if (mimeKind === 'pdf') return true
  return fileName.toLowerCase().endsWith('.pdf')
}
