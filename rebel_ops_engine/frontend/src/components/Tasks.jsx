import React, { useEffect, useState } from 'react'
import { api } from '../api.js'

export default function Tasks() {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    api.tasks()
      .then((data) => { if (!cancelled) setTasks(data) })
      .catch((err) => { if (!cancelled) setError(err.message) })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])

  if (error) return <div className="alert alert-danger">Failed to load tasks: {error}</div>
  if (loading) return <div className="loader">Loading tasks...</div>

  return (
    <div>
      <h2>Generated Tasks</h2>
      <p style={{ color: '#8892a4', marginBottom: 16, fontSize: 13 }}>
        Every routed request creates a task. Security and error events also generate tasks.
      </p>
      <div className="card" style={{ padding: 0, overflowX: 'auto' }}>
        <table>
          <thead>
            <tr>
              <th>Owner</th>
              <th>Team</th>
              <th>Title</th>
              <th>Priority</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {tasks.length === 0 && (
              <tr><td colSpan={5} style={{ textAlign: 'center', padding: 20, color: '#8892a4' }}>No tasks yet. Load demo messages first.</td></tr>
            )}
            {tasks.map((t) => (
              <tr key={t.id}>
                <td style={{ fontWeight: 600 }}>{t.owner}</td>
                <td style={{ fontSize: 12 }}>{t.assigned_team}</td>
                <td>{t.title}</td>
                <td>
                  <span style={{
                    color: t.priority === 'critical' ? '#ef5350'
                         : t.priority === 'high' ? '#ff9800'
                         : t.priority === 'medium' ? '#ffd54f'
                         : '#90a4ae',
                    fontWeight: 600, fontSize: 12,
                  }}>
                    {t.priority}
                  </span>
                </td>
                <td><span className="badge badge-pending">{t.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
