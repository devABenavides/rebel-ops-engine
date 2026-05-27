import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import MorningBriefing from './MorningBriefing.jsx'

describe('MorningBriefing', () => {
  it('shows loading state', () => {
    render(<MorningBriefing />)
    expect(screen.getByText('Generating briefing...')).toBeInTheDocument()
  })

  it('renders greeting', async () => {
    render(<MorningBriefing />)
    expect(await screen.findByText(/Good morning/)).toBeInTheDocument()
    const leia = screen.getAllByText(/General Leia/)
    expect(leia.length).toBeGreaterThanOrEqual(1)
  })

  it('renders stats cards', async () => {
    render(<MorningBriefing />)
    expect(await screen.findByText('Total requests')).toBeInTheDocument()
    expect(await screen.findByText('Completed')).toBeInTheDocument()
    expect(await screen.findByText('Threats blocked')).toBeInTheDocument()
    expect(await screen.findByText('Encrypted')).toBeInTheDocument()
  })

  it('renders delegation sidebar', async () => {
    render(<MorningBriefing />)
    expect(await screen.findByText(/Today's delegation/)).toBeInTheDocument()
  })

  it('renders quick actions', async () => {
    render(<MorningBriefing />)
    expect(await screen.findByText('Quick actions')).toBeInTheDocument()
    expect(await screen.findByText('Run demo scenario')).toBeInTheDocument()
  })

  it('renders connected sources', async () => {
    render(<MorningBriefing />)
    expect(await screen.findByText('Connected sources')).toBeInTheDocument()
    expect(await screen.findByText('Gmail')).toBeInTheDocument()
    expect(await screen.findByText('Calendar')).toBeInTheDocument()
    expect(await screen.findByText('WhatsApp')).toBeInTheDocument()
  })
})
