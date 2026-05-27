import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Briefing from './Briefing.jsx'

describe('Briefing', () => {
  it('shows loading state', () => {
    render(<Briefing />)
    expect(screen.getByText('Generating briefing...')).toBeInTheDocument()
  })

  it('renders briefing content after loading', async () => {
    render(<Briefing />)
    expect(await screen.findByText('Daily Hologram Briefing')).toBeInTheDocument()
    expect(await screen.findByText(/General Leia/)).toBeInTheDocument()
  })

  it('renders refresh button', async () => {
    render(<Briefing />)
    expect(await screen.findByText('Refresh')).toBeInTheDocument()
  })
})
