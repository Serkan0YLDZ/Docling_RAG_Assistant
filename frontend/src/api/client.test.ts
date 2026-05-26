import { describe, expect, it } from 'vitest'
import { isMockMode } from './client'

describe('api client', () => {
  it('uses mock mode by default in tests', () => {
    expect(isMockMode()).toBe(true)
  })
})
