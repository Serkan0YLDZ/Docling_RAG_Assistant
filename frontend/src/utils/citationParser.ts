export interface ParsedCitationRef {
  refIndex: number
  raw: string
}

/** Metin içindeki [1], [2] veya [Sayfa N] referanslarını çıkarır. */
export function parseCitationRefs(text: string): ParsedCitationRef[] {
  const refs: ParsedCitationRef[] = []
  const numeric = /\[\s*(\d+)\s*\]/g
  let match: RegExpExecArray | null
  while ((match = numeric.exec(text)) !== null) {
    refs.push({ refIndex: Number(match[1]), raw: match[0] })
  }
  const pagePattern = /\[Sayfa\s+(\d+)\]/gi
  while ((match = pagePattern.exec(text)) !== null) {
    refs.push({ refIndex: Number(match[1]), raw: match[0] })
  }
  return refs
}

/** Cevap metnini citation chip parçalarına böler. */
export function splitContentWithCitations(
  content: string,
): Array<{ type: 'text' | 'citation'; value: string; refIndex?: number }> {
  const parts: Array<{ type: 'text' | 'citation'; value: string; refIndex?: number }> = []
  const pattern = /(\[\s*\d+\s*\]|\[Sayfa\s+\d+\])/gi
  let lastIndex = 0
  let match: RegExpExecArray | null
  while ((match = pattern.exec(content)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: 'text', value: content.slice(lastIndex, match.index) })
    }
    const num = Number(match[0].replace(/\D/g, ''))
    parts.push({ type: 'citation', value: match[0], refIndex: num })
    lastIndex = match.index + match[0].length
  }
  if (lastIndex < content.length) {
    parts.push({ type: 'text', value: content.slice(lastIndex) })
  }
  return parts.length > 0 ? parts : [{ type: 'text', value: content }]
}
