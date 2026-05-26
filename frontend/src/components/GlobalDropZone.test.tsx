import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { GlobalDropZone } from './GlobalDropZone'

describe('GlobalDropZone', () => {
  it('renders children and hidden file input', () => {
    render(
      <GlobalDropZone onFiles={vi.fn()}>
        <div data-testid="child">İçerik</div>
      </GlobalDropZone>,
    )
    expect(screen.getByTestId('global-drop-zone')).toBeInTheDocument()
    expect(screen.getByTestId('file-input')).toBeInTheDocument()
    expect(screen.getByTestId('child')).toBeInTheDocument()
  })
})
