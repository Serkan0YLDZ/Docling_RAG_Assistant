import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { AppShell } from './AppShell'

describe('AppShell responsive', () => {
  it('shows mobile header actions', async () => {
    const onOpenSidebar = vi.fn()
    const onOpenSource = vi.fn()
    const user = userEvent.setup()
    render(
      <AppShell
        sidebarOpen
        sourceOpen
        onOpenSidebar={onOpenSidebar}
        onOpenSource={onOpenSource}
        sidebar={<span>sb</span>}
        chat={<span>chat</span>}
        source={<span>src</span>}
      />,
    )
    await user.click(screen.getByTestId('open-sidebar'))
    expect(onOpenSidebar).toHaveBeenCalled()
    await user.click(screen.getByTestId('open-source'))
    expect(onOpenSource).toHaveBeenCalled()
  })
})
