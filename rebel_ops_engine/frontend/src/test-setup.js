import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { server } from './mocks/server.js'
import { afterAll, afterEach, beforeAll } from 'vitest'

beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }))
afterEach(() => {
  cleanup()
  server.resetHandlers()
})
afterAll(() => server.close())
