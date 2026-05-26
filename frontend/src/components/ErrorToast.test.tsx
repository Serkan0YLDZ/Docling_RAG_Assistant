import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { ErrorToast } from './ErrorToast'

describe('ErrorToast', () => {
  it('shows error message', () => {
    render(<ErrorToast message="Hata oluştu" onDismiss={vi.fn()} />)
    expect(screen.getByRole('alert')).toHaveTextContent('Hata oluştu')
  })

  it('dismisses on click', async () => {
    const onDismiss = vi.fn()
    const user = userEvent.setup()
    render(<ErrorToast message="Hata" onDismiss={onDismiss} />)
    await user.click(screen.getByLabelText('Kapat'))
    expect(onDismiss).toHaveBeenCalled()
  })

  it('renders nothing when message is null', () => {
    const { container } = render(<ErrorToast message={null} onDismiss={vi.fn()} />)
    expect(container.firstChild).toBeNull()
  })
})
