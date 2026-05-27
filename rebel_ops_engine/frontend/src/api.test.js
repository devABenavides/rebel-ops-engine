import { describe, it, expect } from 'vitest'
import { api } from './api.js'

describe('api', () => {
  it('status returns service info', async () => {
    const res = await api.status()
    expect(res).toHaveProperty('status', 'ok')
    expect(res).toHaveProperty('service')
  })

  it('messages returns a list', async () => {
    const res = await api.messages()
    expect(res.data).toHaveLength(4)
  })

  it('message returns single by id', async () => {
    const res = await api.message('msg-1')
    expect(res).toHaveProperty('id', 'msg-1')
    expect(res).toHaveProperty('sender', 'Han Solo')
  })

  it('agents returns agent list', async () => {
    const res = await api.agents()
    expect(res.agents).toContain('IntakeAgent')
  })

  it('briefing returns text', async () => {
    const res = await api.briefing()
    expect(res.briefing).toContain('General Leia')
  })

  it('calendar returns bookings', async () => {
    const res = await api.calendar()
    expect(res.data).toHaveLength(1)
  })

  it('tasks returns task list', async () => {
    const res = await api.tasks()
    expect(res.data).toHaveLength(2)
  })

  it('trace returns pipeline trace', async () => {
    const res = await api.trace('msg-1')
    expect(res).toHaveProperty('request_id', 'msg-1')
    expect(res.pipeline).toContain('IntakeAgent')
  })

  it('intake posts a message', async () => {
    const res = await api.intake('intergalactic_whatsapp', 'Test Sender', 'Test content')
    expect(res).toHaveProperty('status', 'completed')
  })

  it('demoLoad returns loaded count', async () => {
    const res = await api.demoLoad()
    expect(res.loaded).toBeGreaterThan(0)
  })

  it('reset clears state', async () => {
    const res = await api.reset()
    expect(res).toHaveProperty('status', 'reset')
  })

  it('inbox returns briefing inbox data', async () => {
    const res = await api.inbox()
    expect(res).toHaveProperty('total_messages')
    expect(res).toHaveProperty('needs_attention')
  })

  it('integrations returns integration status', async () => {
    const res = await api.integrations()
    expect(res).toHaveProperty('gmail')
    expect(res).toHaveProperty('calendar')
  })

  it('generateBriefing triggers generation', async () => {
    const res = await api.generateBriefing()
    expect(res).toHaveProperty('status', 'generated')
  })
})
