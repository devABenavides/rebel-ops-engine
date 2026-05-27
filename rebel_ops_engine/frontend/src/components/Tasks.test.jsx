import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Tasks from './Tasks.jsx'

describe('Tasks', () => {
  it('shows loading state', () => {
    render(<Tasks />)
    expect(screen.getByText('Loading tasks...')).toBeInTheDocument()
  })

  it('renders tasks heading', async () => {
    render(<Tasks />)
    expect(await screen.findByText('Generated Tasks')).toBeInTheDocument()
  })

  it('renders task table headers', async () => {
    render(<Tasks />)
    expect(await screen.findByText('Owner')).toBeInTheDocument()
    expect(await screen.findByText('Team')).toBeInTheDocument()
    expect(await screen.findByText('Title')).toBeInTheDocument()
    expect(await screen.findByText('Priority')).toBeInTheDocument()
    expect(await screen.findByText('Status')).toBeInTheDocument()
  })

  it('renders task rows', async () => {
    render(<Tasks />)
    expect(await screen.findByText('Han Solo')).toBeInTheDocument()
    expect(await screen.findByText('Arrange fuel delivery')).toBeInTheDocument()
  })
})
