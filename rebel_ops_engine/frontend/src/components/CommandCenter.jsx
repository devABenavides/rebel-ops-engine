import React, { useEffect, useState } from 'react'
import { api } from '../api.js'

const CATEGORY_ICONS = {
  calendar_booking: '\uD83D\uDCC5',
  planet_help: '\uD83C\uDF0D',
  recruitment: '\uD83E\uDD4D',
  soldier_support: '\uD83C\uDF96\uFE0F',
  population_training: '\uD83C\uDF93',
  logistics: '\uD83D\uDE9A',
  investor_partner: '\uD83E\uDD1D',
  urgent_security: '\u26A1',
  jedi_training_diplomacy: '\uD83E\uDDD9',
  ahsoka_special_mission: '\uD83D\uDD75\uFE0F',
  yoda_encrypted_strategy: '\uD83D\uDD12',
  field_operations: '\uD83C\uDFC6',
  special_protection: '\uD83D\uDEE1\uFE0F',
  data_support: '\uD83D\uDCCA',
  other: '\u2753',
}

const CATEGORY_LABELS = {
  calendar_booking: 'Calendar Booking',
  planet_help: 'Planet Help',
  recruitment: 'Recruitment',
  soldier_support: 'Soldier Support',
  population_training: 'Population Training',
  logistics: 'Logistics',
  investor_partner: 'Investor & Partner',
  urgent_security: 'Urgent Security',
  jedi_training_diplomacy: 'Jedi Training & Diplomacy',
  ahsoka_special_mission: 'Ahsoka Special Mission',
  yoda_encrypted_strategy: 'Yoda Encrypted Strategy',
  field_operations: 'Field Operations',
  special_protection: 'Special Protection',
  data_support: 'Data Support',
  other: 'Other',
}

function traceActionIcon(action) {
  if (['quarantined', 'rejected', 'error_logged'].includes(action)) return '\u26D4'
  if (action === 'encrypted') return '\uD83D\uDD12'
  if (action === 'classified') return '\uD83E\uDD16'
  if (action === 'routed') return '\uD83D\uDD01'
  if (action === 'notified') return '\uD83D\uDD14'
  if (action === 'booked') return '\uD83D\uDCC5'
  if (action === 'stored') return '\uD83D\uDCBE'
  return '\u25B6\uFE0F'
}

function traceActionLabel(action) {
  switch (action) {
    case 'validated': return 'Validated'
    case 'quarantined': return 'BLOCKED - High Risk'
    case 'flagged': return 'Flagged - Medium Risk'
    case 'cleared': return 'Cleared - Low Risk'
    case 'classified': return 'Classified'
    case 'routed': return 'Routed'
    case 'skipped': return 'Skipped'
    case 'encrypted': return 'Encrypted'
    case 'notified': return 'Notified'
    case 'booked': return 'Calendar Booked'
    case 'stored': return 'Stored'
    case 'quarantine_logged': return 'Security Task Created'
    case 'error_logged': return 'Error Task Created'
    case 'passed': return 'Passed'
    case 'rejected': return 'Rejected'
    default: return action
  }
}

function FlowCard({ msg }) {
  const trace = msg.trace || []
  const label = CATEGORY_LABELS[msg.category] || msg.category
  const isQuarantined = msg.status === 'quarantined'
  const isEncrypted = msg.encrypted

  return (
    <div className="flow-card" style={{
      border: `1px solid ${isQuarantined ? '#6b1a1a' : '#2a3346'}`,
    }}>
      <div className="flow-card-header" style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10,
      }}>
        <div>
          <div style={{ fontSize: 12, color: '#8892a4' }}>
            {msg.channel === 'intergalactic_whatsapp' ? '\uD83D\uDCAC Intergalactic WhatsApp' : '\u2709\uFE0F Hologram Email'}
            {' \u2022 '}
            {new Date(msg.timestamp || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
          <div style={{ fontWeight: 700, fontSize: 15, marginTop: 2, color: '#f0f0f0' }}>{msg.sender}</div>
        </div>
        <div style={{
          padding: '3px 10px', borderRadius: 4, fontSize: 11, fontWeight: 700, whiteSpace: 'nowrap',
          ...(isQuarantined ? { background: '#3d1b1b', color: '#ef5350' }
            : isEncrypted ? { background: '#2d2b1b', color: '#ffd54f' }
            : msg.status === 'completed' ? { background: '#1b3d2e', color: '#4caf7d' }
            : msg.status === 'error' ? { background: '#3d1b1b', color: '#ef5350' }
            : msg.status === 'security_review' ? { background: '#2d2b1b', color: '#ff9800' }
            : { background: '#1e2435', color: '#90a4ae' }),
        }}>
          {isQuarantined ? '\u26D4 QUARANTINED'
            : isEncrypted ? '\uD83D\uDD12 ENCRYPTED'
            : msg.status === 'error' ? '\u26A0 ERROR'
            : msg.status === 'security_review' ? '\u2753 REVIEW'
            : msg.status.toUpperCase()}
        </div>
      </div>

      <div style={{ fontSize: 13, color: '#c8d6e5', lineHeight: 1.5, marginBottom: 10, padding: '8px 10px', background: '#0b0e14', borderRadius: 4 }}>
        {isEncrypted ? '[Encrypted Yoda Strategy - Content Hidden]' : (msg.content && msg.content.length > 200 ? msg.content.slice(0, 200) + '...' : msg.content)}
      </div>

      {isQuarantined ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 10px', background: '#1a0d0d', borderRadius: 4, color: '#ef5350', fontSize: 12 }}>
          <span style={{ fontSize: 18, fontWeight: 700 }}>{'\u26D4'}</span>
          <div>
            <div style={{ fontWeight: 700 }}>Security Threat Blocked</div>
            <div style={{ color: '#ff9090', marginTop: 2 }}>{msg.error || 'High-risk content detected'}</div>
            {msg.dark_side_indicators?.length > 0 && (
              <div style={{ color: '#8892a4', marginTop: 2 }}>Indicators: {msg.dark_side_indicators.join(', ')}</div>
            )}
          </div>
        </div>
      ) : (
        <div className="flow-card-trace">
          {trace.filter(t => t.action !== 'passed' && t.action !== 'skipped').map((t, i) => (
            <div key={i} className="trace-step">
              <div className="trace-line">
                <span className="trace-icon">{traceActionIcon(t.action)}</span>
                <span className="trace-action">{traceActionLabel(t.action)}</span>
                {t.details?.category && <span className="trace-info">{CATEGORY_LABELS[t.details.category] || t.details.category}</span>}
                {t.details?.owner && <span className="trace-info">{'\u2192'} {t.details.owner}</span>}
                {t.details?.team && <span className="trace-info">({t.details.team})</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function CommandCenter() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState('all')

  const load = () => {
    setLoading(true)
    api.messages()
      .then(setMessages)
      .catch(() => setError('Failed to load messages'))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const filtered = filter === 'all' ? messages
    : filter === 'leia' ? messages.filter(m => m.requires_leia)
    : filter === 'quarantined' ? messages.filter(m => m.status === 'quarantined')
    : messages

  const leiaItems = messages.filter(m => m.requires_leia)
  const quarantined = messages.filter(m => m.status === 'quarantined')
  const completed = messages.filter(m => m.status === 'completed')
  const encrypted = messages.filter(m => m.encrypted)

  if (error) return <div className="alert alert-danger">{error}</div>

  return (
    <div style={{ display: 'flex', gap: 20 }}>
      <div style={{ flex: 1, minWidth: 0 }}>
        <h2 style={{ marginBottom: 4 }}>Command Center</h2>
        <p style={{ color: '#8892a4', fontSize: 13, marginBottom: 20 }}>
          See every request processed by the Rebellion today.
        </p>

        <div className="stats-grid" style={{ marginBottom: 20 }}>
          <div className="card"><h3>Total Requests</h3><div className="value">{messages.length}</div></div>
          <div className="card"><h3>Completed</h3><div className="value" style={{ color: '#4caf7d' }}>{completed.length}</div></div>
          <div className="card"><h3>{'\u26D4'} Threats Blocked</h3><div className="value" style={{ color: '#ef5350' }}>{quarantined.length}</div></div>
          <div className="card"><h3>{'\uD83D\uDD12'} Encrypted</h3><div className="value" style={{ color: '#ffd54f' }}>{encrypted.length}</div></div>
        </div>

        <div className="btn-group">
          <button className={`btn ${filter === 'all' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setFilter('all')}>All</button>
          <button className={`btn ${filter === 'leia' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setFilter('leia')}>Needs Leia ({leiaItems.length})</button>
          <button className={`btn ${filter === 'quarantined' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setFilter('quarantined')}>Threats ({quarantined.length})</button>
          <button className="btn btn-success" onClick={load} disabled={loading}>Refresh</button>
        </div>

        {loading ? <div className="loader">Loading...</div> : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {filtered.length === 0 && (
              <div className="card" style={{ textAlign: 'center', color: '#8892a4', padding: 40 }}>
                No requests yet. Click &quot;Load Demo&quot; in the sidebar to see the system in action.
              </div>
            )}
            {filtered.map(m => <FlowCard key={m.id} msg={m} />)}
          </div>
        )}
      </div>

      {filter === 'all' && (
        <div style={{ width: 280, flexShrink: 0 }}>
          <div className="card" style={{ position: 'sticky', top: 24 }}>
            <h3 style={{ marginBottom: 12 }}>{'\u26A0\uFE0F'} Needs Your Attention</h3>
            {leiaItems.length === 0 ? (
              <div style={{ color: '#4caf7d', fontSize: 13 }}>{'\u2705'} No items require your decision right now.</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {leiaItems.map(m => (
                  <div key={m.id} style={{ padding: '8px 10px', background: '#1a2740', borderRadius: 4 }}>
                    <div style={{ fontWeight: 600, fontSize: 13 }}>{m.sender}</div>
                    <div style={{ color: '#8892a4', fontSize: 11, marginTop: 2 }}>
                      {CATEGORY_LABELS[m.category] || m.category}
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div style={{ marginTop: 16, paddingTop: 12, borderTop: '1px solid #2a3346' }}>
              <h3 style={{ marginBottom: 8 }}>{'\uD83D\uDCCB'} Today&apos;s Delegation</h3>
              {(() => {
                const counts = {}
                messages.forEach(m => {
                  if (m.owner) counts[m.owner] = (counts[m.owner] || 0) + 1
                })
                return Object.entries(counts).sort((a, b) => b[1] - a[1]).map(([owner, count]) => (
                  <div key={owner} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, padding: '4px 0', color: '#a0aaba' }}>
                    <span>{owner}</span>
                    <span style={{ fontWeight: 700, color: '#4fc3f7' }}>{count}</span>
                  </div>
                ))
              })()}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
