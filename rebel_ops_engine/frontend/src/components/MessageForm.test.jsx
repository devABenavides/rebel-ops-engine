import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import MessageForm from './MessageForm.jsx'

describe('MessageForm', () => {
  it('renders form fields', () => {
    render(<MessageForm />)
    expect(screen.getByText('Channel')).toBeInTheDocument()
    expect(screen.getByText('Sender')).toBeInTheDocument()
    expect(screen.getByText('Message Content')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Send Message' })).toBeInTheDocument()
  })

  it('submit button is disabled when fields empty', () => {
    render(<MessageForm />)
    expect(screen.getByRole('button', { name: 'Send Message' })).toBeDisabled()
  })

  it('submit button enables when fields filled', async () => {
    const user = userEvent.setup()
    render(<MessageForm />)
    await user.type(screen.getByPlaceholderText('e.g. Han Solo'), 'Test Sender')
    await user.type(screen.getByPlaceholderText('Type your message...'), 'Test content')
    expect(screen.getByRole('button', { name: 'Send Message' })).toBeEnabled()
  })

  it('shows success message on submission', async () => {
    const user = userEvent.setup()
    render(<MessageForm />)
    await user.type(screen.getByPlaceholderText('e.g. Han Solo'), 'Leia')
    await user.type(screen.getByPlaceholderText('Type your message...'), 'Need supplies for base')
    await user.click(screen.getByRole('button', { name: 'Send Message' }))
    expect(await screen.findByText('Message processed successfully.')).toBeInTheDocument()
  })

  it('shows category and owner after submission', async () => {
    const user = userEvent.setup()
    render(<MessageForm />)
    await user.type(screen.getByPlaceholderText('e.g. Han Solo'), 'Leia')
    await user.type(screen.getByPlaceholderText('Type your message...'), 'Need supplies for base')
    await user.click(screen.getByRole('button', { name: 'Send Message' }))
    expect(await screen.findByText('logistics')).toBeInTheDocument()
    expect(await screen.findByText('Han Solo')).toBeInTheDocument()
  })

  it('calls onMessageSent callback after submit', async () => {
    const onMessageSent = vi.fn()
    const user = userEvent.setup()
    render(<MessageForm onMessageSent={onMessageSent} />)
    await user.type(screen.getByPlaceholderText('e.g. Han Solo'), 'Leia')
    await user.type(screen.getByPlaceholderText('Type your message...'), 'Need supplies')
    await user.click(screen.getByRole('button', { name: 'Send Message' }))
    expect(await screen.findByText('Message processed successfully.')).toBeInTheDocument()
    expect(onMessageSent).toHaveBeenCalledTimes(1)
  })
})
