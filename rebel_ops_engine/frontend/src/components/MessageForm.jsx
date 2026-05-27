import React, { useState, useEffect } from 'react'
import { api } from '../api.js'

export default function MessageForm({ onMessageSent }) {
  const [channel, setChannel] = useState('intergalactic_whatsapp')
  const [sender, setSender] = useState('')
  const [content, setContent] = useState('')
  const [contact, setContact] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [notification, setNotification] = useState(null)

  useEffect(() => {
    if (!notification) return
    const id = setTimeout(() => setNotification(null), 4000)
    return () => clearTimeout(id)
  }, [notification])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!sender.trim() || !content.trim()) return
    setLoading(true)
    setResult(null)
    try {
      const res = await api.intake(channel, sender, content, contact)
      setResult({ ok: true, data: res })
      setNotification({ kind: 'success', message: `Sent — ${res.category || 'request'} routed to ${res.owner || 'team'} (${res.status})` })
      setSender('')
      setContent('')
      setContact('')
      if (onMessageSent) onMessageSent()
    } catch (err) {
      setResult({ ok: false, error: err.message })
      setNotification({ kind: 'error', message: `Failed: ${err.message}` })
    } finally {
      setLoading(false)
    }
  }

  const handleChannelChange = (e) => {
    setChannel(e.target.value)
    setResult(null)
    setLoading(false)
  }

  const channelLabel = (ch) =>
    ch === 'intergalactic_whatsapp' ? 'Intergalactic WhatsApp' : 'Hologram Email'

  return (
    <div>
      <h2>Send Message</h2>

      {notification && (
        <div style={{
          padding: '10px 14px', borderRadius: 6, marginBottom: 12, fontSize: 13,
          background: notification.kind === 'success' ? 'var(--rebel-bg, #e8f5e9)' : 'var(--sith-bg, #ffebee)',
          color: notification.kind === 'success' ? 'var(--rebel, #2e7d32)' : 'var(--sith, #c62828)',
          border: `1px solid ${notification.kind === 'success' ? 'var(--rebel, #2e7d32)' : 'var(--sith, #c62828)'}`,
          opacity: notification ? 1 : 0, transition: 'opacity 0.3s',
        }}>
          {notification.kind === 'success' ? '\u2705' : '\u274C'} {notification.message}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label>Channel</label>
            <select value={channel} onChange={handleChannelChange}>
              <option value="intergalactic_whatsapp">Intergalactic WhatsApp</option>
              <option value="hologram_email">Hologram Email</option>
            </select>
          </div>
          <div className="form-group">
            <label>Sender</label>
            <input value={sender} onChange={(e) => setSender(e.target.value)} placeholder="e.g. Han Solo" />
          </div>
        </div>
        {channel === 'intergalactic_whatsapp' && (
          <div className="form-group">
            <label>Phone Number (for WhatsApp delivery)</label>
            <input value={contact} onChange={(e) => setContact(e.target.value)} placeholder="e.g. 15551234567" type="tel" />
          </div>
        )}
        <div className="form-group">
          <label>Message Content</label>
          <textarea value={content} onChange={(e) => setContent(e.target.value)} placeholder="Type your message..." />
        </div>
        <button className="btn btn-primary" type="submit" disabled={loading || !sender.trim() || !content.trim()}>
          {loading ? 'Sending...' : 'Send Message'}
        </button>
      </form>

      {result && result.ok && (
        <div className="card" style={{ marginTop: 16 }}>
          <div>
            <div className="alert alert-success">Message processed successfully.</div>
            <table>
              <thead><tr><th>Field</th><th>Value</th></tr></thead>
              <tbody>
                <tr><td>Status</td><td>{result.data.status}</td></tr>
                <tr><td>Channel</td><td>{channelLabel(result.data.channel)}</td></tr>
                <tr><td>Category</td><td>{result.data.category || '-'}</td></tr>
                <tr><td>Owner</td><td>{result.data.owner || '-'}</td></tr>
                <tr><td>Risk Score</td><td>{result.data.risk_score}</td></tr>
                <tr><td>Encrypted</td><td>{result.data.encrypted ? 'Yes' : 'No'}</td></tr>
                {result.data.error && <tr><td>Error</td><td style={{ color: 'var(--sith)' }}>{result.data.error}</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      )}
      {result && !result.ok && (
        <div className="card" style={{ marginTop: 16 }}>
          <div className="alert alert-danger">Failed: {result.error}</div>
        </div>
      )}
    </div>
  )
}
