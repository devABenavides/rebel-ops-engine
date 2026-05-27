import React from 'react'
import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ThemeProvider, useTheme } from '../ThemeContext.jsx'

function TestConsumer() {
  const { theme, toggleTheme } = useTheme()
  return (
    <div>
      <span data-testid="theme-value">{theme}</span>
      <button onClick={toggleTheme}>Toggle</button>
    </div>
  )
}

describe('ThemeContext', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('defaults to light theme', () => {
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>
    )
    expect(screen.getByTestId('theme-value')).toHaveTextContent('light')
  })

  it('toggles theme on button click', async () => {
    const user = userEvent.setup()
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>
    )
    await user.click(screen.getByText('Toggle'))
    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark')
  })

  it('toggles back to light on second click', async () => {
    const user = userEvent.setup()
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>
    )
    await user.click(screen.getByText('Toggle'))
    await user.click(screen.getByText('Toggle'))
    expect(screen.getByTestId('theme-value')).toHaveTextContent('light')
  })

  it('persists theme to localStorage', async () => {
    const user = userEvent.setup()
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>
    )
    await user.click(screen.getByText('Toggle'))
    expect(localStorage.getItem('rebel-theme')).toBe('dark')
  })

  it('sets data-theme attribute on document', async () => {
    const user = userEvent.setup()
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>
    )
    await user.click(screen.getByText('Toggle'))
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
  })
})
