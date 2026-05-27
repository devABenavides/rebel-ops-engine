import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ThemeProvider } from './ThemeContext.jsx'
import App from './App.jsx'

describe('App', () => {
  it('renders sidebar nav', () => {
    render(
      <ThemeProvider>
        <App />
      </ThemeProvider>
    )
    expect(screen.getByText('REBEL OPS')).toBeInTheDocument()
    const morning = screen.getAllByText(/Morning Briefing/)
    expect(morning.length).toBeGreaterThanOrEqual(1)
    const command = screen.getAllByText(/Command Center/)
    expect(command.length).toBeGreaterThanOrEqual(1)
    const arch = screen.getAllByText(/Architecture/)
    expect(arch.length).toBeGreaterThanOrEqual(1)
    const brief = screen.getAllByText(/Briefing/)
    expect(brief.length).toBeGreaterThanOrEqual(1)
    const msg = screen.getAllByText(/Send Message/)
    expect(msg.length).toBeGreaterThanOrEqual(1)
    const team = screen.getAllByText(/Team Directory/)
    expect(team.length).toBeGreaterThanOrEqual(1)
    const cal = screen.getAllByText(/Calendar/)
    expect(cal.length).toBeGreaterThanOrEqual(1)
    const task = screen.getAllByText(/Tasks/)
    expect(task.length).toBeGreaterThanOrEqual(1)
  })

  it('renders theme toggle button', () => {
    render(
      <ThemeProvider>
        <App />
      </ThemeProvider>
    )
    expect(screen.getByText('Dark theme')).toBeInTheDocument()
  })

  it('renders Load Demo and Reset buttons', () => {
    render(
      <ThemeProvider>
        <App />
      </ThemeProvider>
    )
    expect(screen.getByText('Load Demo')).toBeInTheDocument()
    expect(screen.getByText('Reset State')).toBeInTheDocument()
  })
})
