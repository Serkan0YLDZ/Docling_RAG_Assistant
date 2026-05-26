/** Scroll container içinde sayfa öğesinin üst konumunu hesaplar. */
export function getPageScrollTop(container: HTMLElement, pageEl: HTMLElement): number {
  const containerRect = container.getBoundingClientRect()
  const pageRect = pageEl.getBoundingClientRect()
  return pageRect.top - containerRect.top + container.scrollTop
}

/** Görünür alanda en baskın sayfa numarasını bulur. */
export function pickVisiblePage(
  container: HTMLElement,
  pageCount: number,
): number {
  const containerRect = container.getBoundingClientRect()
  const midY = containerRect.top + containerRect.height * 0.35

  let bestPage = 1
  let bestDist = Number.POSITIVE_INFINITY

  for (let page = 1; page <= pageCount; page += 1) {
    const el = container.querySelector<HTMLElement>(`[data-page-number="${page}"]`)
    if (!el) continue
    const rect = el.getBoundingClientRect()
    const pageMid = rect.top + rect.height / 2
    const dist = Math.abs(pageMid - midY)
    if (dist < bestDist) {
      bestDist = dist
      bestPage = page
    }
  }

  return bestPage
}
