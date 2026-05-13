import React, { useEffect, useState } from 'react'
import { api } from '../api.js'

export default function Calendar() {
  const [bookings, setBookings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    api.calendar()
      .then((data) => { if (!cancelled) setBookings(data) })
      .catch((err) => { if (!cancelled) setError(err.message) })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])

  if (error) return <div className="alert alert-danger">Failed to load calendar: {error}</div>
  if (loading) return <div className="loader">Loading calendar...</div>

  return (
    <div>
      <h2>Public Calendar</h2>
      <div className="alert alert-info">
        Private Leia calendar entries are redacted per Rebel security policy.
      </div>
      <div className="card" style={{ padding: 0, overflowX: 'auto' }}>
        <table>
          <thead><tr><th>Requestor</th><th>Subject</th></tr></thead>
          <tbody>
            {bookings.length === 0 && (
              <tr><td colSpan={2} style={{ textAlign: 'center', padding: 20, color: '#8892a4' }}>No public bookings</td></tr>
            )}
            {bookings.map((b) => (
              <tr key={b.message_id}>
                <td style={{ fontWeight: 600 }}>{b.requestor}</td>
                <td>{b.subject}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
