import React, { useState } from 'react'
import { api } from '../api.js'

export default function MessageForm({ onMessageSent }) {
  const [channel, setChannel] = useState('intergalactic_whatsapp')
  const [sender, setSender] = useState('')
  const [content, setContent] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!sender.trim() || !content.trim()) return
    setLoading(true)
    setResult(null)
    try {
      const res = await api.intake(channel, sender, content)
      setResult({ ok: true, data: res })
      setSender('')
      setContent('')
      if (onMessageSent) onMessageSent()
    } catch (err) {
      setResult({ ok: false, error: err.message })
    }
    setLoading(false)
  }

  return (
    <div>
      <h2>Send Message</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label>Channel</label>
            <select value={channel} onChange={(e) => setChannel(e.target.value)}>
              <option value="intergalactic_whatsapp">Intergalactic WhatsApp</option>
              <option value="hologram_email">Hologram Email</option>
            </select>
          </div>
          <div className="form-group">
            <label>Sender</label>
            <input value={sender} onChange={(e) => setSender(e.target.value)} placeholder="e.g. Han Solo" />
          </div>
        </div>
        <div className="form-group">
          <label>Message Content</label>
          <textarea value={content} onChange={(e) => setContent(e.target.value)} placeholder="Type your message..." />
        </div>
        <button className="btn btn-primary" type="submit" disabled={loading || !sender.trim() || !content.trim()}>
          {loading ? 'Sending...' : 'Send Message'}
        </button>
      </form>

      {result && (
        <div className="card" style={{ marginTop: 16 }}>
          {result.ok ? (
            <div>
              <div className="alert alert-success">Message processed successfully.</div>
              <table>
                <thead><tr><th>Field</th><th>Value</th></tr></thead>
                <tbody>
                  <tr><td>Status</td><td>{result.data.status}</td></tr>
                  <tr><td>Category</td><td>{result.data.category || '-'}</td></tr>
                  <tr><td>Owner</td><td>{result.data.owner || '-'}</td></tr>
                  <tr><td>Risk Score</td><td>{result.data.risk_score}</td></tr>
                  <tr><td>Encrypted</td><td>{result.data.encrypted ? 'Yes' : 'No'}</td></tr>
                  {result.data.error && <tr><td>Error</td><td style={{ color: '#ef5350' }}>{result.data.error}</td></tr>}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="alert alert-danger">Failed: {result.error}</div>
          )}
        </div>
      )}
    </div>
  )
}
