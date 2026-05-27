import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Calendar from './Calendar.jsx'

describe('Calendar', () => {
  it('shows loading state', () => {
    render(<Calendar />)
    expect(screen.getByText('Loading calendar...')).toBeInTheDocument()
  })

  it('renders calendar heading', async () => {
    render(<Calendar />)
    expect(await screen.findByText('Public Calendar')).toBeInTheDocument()
  })

  it('shows privacy notice', async () => {
    render(<Calendar />)
    expect(await screen.findByText(/Private Leia calendar entries are redacted/)).toBeInTheDocument()
  })

  it('renders booking rows', async () => {
    render(<Calendar />)
    expect(await screen.findByText('Bail Organa')).toBeInTheDocument()
    expect(await screen.findByText('Weekly strategy meeting')).toBeInTheDocument()
  })
})
