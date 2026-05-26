import { describe, expect, it } from 'vitest'
import { getPageScrollTop, pickVisiblePage } from './pdfViewerScroll'

describe('pdfViewerScroll', () => {
  it('pickVisiblePage chooses page nearest viewport center band', () => {
    const container = document.createElement('div')
    Object.defineProperty(container, 'clientHeight', { value: 400, configurable: true })
    container.getBoundingClientRect = () =>
      ({
        top: 100,
        left: 0,
        width: 400,
        height: 400,
        bottom: 500,
        right: 400,
      }) as DOMRect

    const page1 = document.createElement('div')
    page1.dataset.pageNumber = '1'
    page1.getBoundingClientRect = () =>
      ({ top: 80, height: 100, bottom: 180 }) as DOMRect

    const page2 = document.createElement('div')
    page2.dataset.pageNumber = '2'
    page2.getBoundingClientRect = () =>
      ({ top: 220, height: 100, bottom: 320 }) as DOMRect

    container.append(page1, page2)
    expect(pickVisiblePage(container, 2)).toBe(2)
  })

  it('getPageScrollTop uses container-relative offset', () => {
    const container = document.createElement('div')
    container.scrollTop = 0
    container.getBoundingClientRect = () =>
      ({ top: 50, left: 0, width: 400, height: 400, bottom: 450, right: 400 }) as DOMRect

    const page = document.createElement('div')
    page.getBoundingClientRect = () =>
      ({ top: 250, left: 0, width: 400, height: 500, bottom: 750, right: 400 }) as DOMRect

    expect(getPageScrollTop(container, page)).toBe(200)
  })
})
