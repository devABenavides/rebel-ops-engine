import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Owners from './Owners.jsx'

describe('Owners', () => {
  it('renders page header', () => {
    render(<Owners />)
    expect(screen.getByText('Team Directory')).toBeInTheDocument()
  })

  it('renders all owner cards', () => {
    render(<Owners />)
    expect(screen.getByText('General Leia')).toBeInTheDocument()
    expect(screen.getByText('C-3PO')).toBeInTheDocument()
    expect(screen.getByText('Yoda')).toBeInTheDocument()
    expect(screen.getByText('Han Solo')).toBeInTheDocument()
    expect(screen.getByText('Chewbacca')).toBeInTheDocument()
    expect(screen.getByText('R2-D2')).toBeInTheDocument()
  })

  it('renders how it works section', () => {
    render(<Owners />)
    expect(screen.getByText('How It Works')).toBeInTheDocument()
  })

  it('renders workflow role labels', () => {
    render(<Owners />)
    const labels = screen.getAllByText('Workflow Role')
    expect(labels.length).toBeGreaterThan(10)
  })

  it('renders business meaning labels', () => {
    render(<Owners />)
    const labels = screen.getAllByText('Business Meaning')
    expect(labels.length).toBeGreaterThan(10)
  })
})
