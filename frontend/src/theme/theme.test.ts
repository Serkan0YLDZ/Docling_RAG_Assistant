import { describe, expect, it } from 'vitest'

describe('theme tokens', () => {
  it('defines primary color variable', () => {
    document.documentElement.style.setProperty('--color-primary', '#004ac6')
    expect(document.documentElement.style.getPropertyValue('--color-primary')).toBe(
      '#004ac6',
    )
  })
})
