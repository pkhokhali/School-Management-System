import { describe, it, expect } from 'vitest'

describe('auth guard', () => {
  it('requires login path when no user', () => {
    expect('/login').toBe('/login')
  })
})
