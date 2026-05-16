const BASE = '/api'
const TIMEOUT_MS = 15000

async function request(method, path, body, signal, timeoutMs) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), timeoutMs || TIMEOUT_MS)

  const fetchSignal = signal || controller.signal

  try {
    const res = await fetch(`${BASE}${path}`, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal: fetchSignal,
    })
    clearTimeout(timeout)

    const ct = res.headers.get('content-type') || ''
    const data = ct.includes('application/json') ? await res.json() : await res.text()

    if (!res.ok) {
      const msg = typeof data === 'object' ? (data.error || data.message || JSON.stringify(data)) : data
      throw new Error(msg || `Request failed: ${res.status}`)
    }
    return data
  } catch (err) {
    clearTimeout(timeout)
    if (err.name === 'AbortError') throw new Error('Request timed out')
    throw err
  }
}

export const api = {
  status: (signal) => request('GET', '/', undefined, signal),
  messages: (signal) => request('GET', '/messages', undefined, signal),
  message: (id, signal) => request('GET', `/messages/${id}`, undefined, signal),
  agents: (signal) => request('GET', '/agents', undefined, signal),
  briefing: (signal) => request('GET', '/briefing', undefined, signal),
  calendar: (signal) => request('GET', '/calendar', undefined, signal),
  tasks: (signal) => request('GET', '/tasks', undefined, signal),
  trace: (id, signal) => request('GET', `/requests/${id}/trace`, undefined, signal),
  intake: (channel, sender, content, signal) =>
    request('POST', '/intake', { channel, sender, content }, signal),
  demoLoad: (signal) => request('POST', '/demo/load', undefined, signal, 60000),
  reset: (signal) => request('POST', '/reset', undefined, signal),
  inbox: (signal) => request('GET', '/briefing/inbox', undefined, signal),
  integrations: (signal) => request('GET', '/integrations', undefined, signal),
  generateBriefing: (signal) => request('POST', '/briefings/generate', undefined, signal),
}
