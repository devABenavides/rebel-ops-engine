import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import WorkflowGraph from './WorkflowGraph.jsx'

describe('WorkflowGraph', () => {
  it('renders architecture header', () => {
    render(<WorkflowGraph />)
    expect(screen.getByText('System Architecture')).toBeInTheDocument()
  })

  it('renders all phase labels', () => {
    render(<WorkflowGraph />)
    expect(screen.getAllByText('Ingestion').length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText('Security Scan')).toBeInTheDocument()
    expect(screen.getByText('Classification')).toBeInTheDocument()
    expect(screen.getByText('Routing Engine')).toBeInTheDocument()
    expect(screen.getByText('Delivery')).toBeInTheDocument()
  })

  it('renders pipeline description', () => {
    render(<WorkflowGraph />)
    const descriptions = screen.getAllByText(/Click any component to learn/)
    expect(descriptions.length).toBeGreaterThanOrEqual(1)
  })

  it('renders ingestion phase body expanded by default', () => {
    render(<WorkflowGraph />)
    const intakeLabels = screen.getAllByText('Request Intake')
    expect(intakeLabels.length).toBeGreaterThanOrEqual(1)
  })

  it('clicking Security Scan phase header reveals branch paths', async () => {
    const user = userEvent.setup()
    render(<WorkflowGraph />)
    await user.click(screen.getByText('Security Scan'))
    expect(screen.getByText('Safe — Risk < 50')).toBeInTheDocument()
    expect(screen.getByText('Threat — Risk \u2265 50')).toBeInTheDocument()
  })

  it('clicking Routing Engine phase header reveals destinations', async () => {
    const user = userEvent.setup()
    render(<WorkflowGraph />)
    await user.click(screen.getByText('Routing Engine'))
    expect(screen.getByText(/Routing destinations/)).toBeInTheDocument()
    expect(screen.getByText('General Leia')).toBeInTheDocument()
    expect(screen.getByText('Han Solo')).toBeInTheDocument()
    expect(screen.getByText('Master Yoda')).toBeInTheDocument()
    expect(screen.getByText('Ahsoka Tano')).toBeInTheDocument()
    expect(screen.getByText('R2-D2')).toBeInTheDocument()
  })
})
