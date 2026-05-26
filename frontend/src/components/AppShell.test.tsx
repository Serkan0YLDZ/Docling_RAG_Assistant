import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { AppShell } from './AppShell'

describe('AppShell', () => {
  it('renders three regions', () => {
    render(
      <AppShell
        sidebarOpen
        sourceOpen
        sidebar={<div data-testid="sb">S</div>}
        chat={<div data-testid="ch">C</div>}
        source={<div data-testid="so">O</div>}
      />,
    )
    expect(screen.getByTestId('app-shell')).toBeInTheDocument()
    expect(screen.getByTestId('sb')).toBeInTheDocument()
    expect(screen.getByTestId('ch')).toBeInTheDocument()
    expect(screen.getByTestId('so')).toBeInTheDocument()
  })
})
