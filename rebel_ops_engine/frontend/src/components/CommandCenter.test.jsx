import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import CommandCenter from './CommandCenter.jsx'

describe('CommandCenter', () => {
  it('shows loading state initially', () => {
    render(<CommandCenter />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders command center heading', async () => {
    render(<CommandCenter />)
    expect(await screen.findByText('Command Center')).toBeInTheDocument()
  })

  it('displays total requests count', async () => {
    render(<CommandCenter />)
    expect(await screen.findByText('Total Requests')).toBeInTheDocument()
  })

  it('displays stats grid', async () => {
    render(<CommandCenter />)
    expect(await screen.findByText('Completed')).toBeInTheDocument()
    expect(await screen.findByText(/Threats Blocked/)).toBeInTheDocument()
    const encrypted = screen.getAllByText(/Encrypted/)
    expect(encrypted.length).toBeGreaterThanOrEqual(1)
  })

  it('renders filter buttons', async () => {
    render(<CommandCenter />)
    expect(await screen.findByText('All')).toBeInTheDocument()
    expect(await screen.findByText('Refresh')).toBeInTheDocument()
  })

  it('renders message cards from API', async () => {
    render(<CommandCenter />)
    expect(await screen.findByText('Han Solo')).toBeInTheDocument()
    expect(await screen.findByText('Darth Vader')).toBeInTheDocument()
  })

  it('shows quarantine badge for threats', async () => {
    render(<CommandCenter />)
    expect(await screen.findByText(/QUARANTINED/)).toBeInTheDocument()
  })

  it('shows encrypted badge', async () => {
    render(<CommandCenter />)
    expect(await screen.findByText(/ENCRYPTED/)).toBeInTheDocument()
  })

  it('shows needs attention sidebar section', async () => {
    render(<CommandCenter />)
    expect(await screen.findByText(/Needs Your Attention/)).toBeInTheDocument()
  })
})
