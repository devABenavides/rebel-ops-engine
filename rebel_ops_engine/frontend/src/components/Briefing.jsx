import React, { useEffect, useState } from 'react'
import { api } from '../api.js'

export default function Briefing() {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = () => {
    setLoading(true)
    api.briefing()
      .then((data) => setText(data.briefing))
      .catch(() => setError('Failed to load briefing'))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  if (error) return <div className="alert alert-danger">{error}</div>
  if (loading) return <div className="loader">Generating briefing...</div>

  return (
    <div>
      <h2>Daily Hologram Briefing</h2>
      <div className="btn-group">
        <button className="btn btn-primary" onClick={load}>Refresh</button>
      </div>
      <div className="card">
        <div className="briefing">{text}</div>
      </div>
    </div>
  )
}
