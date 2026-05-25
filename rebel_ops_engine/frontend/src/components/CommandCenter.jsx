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


function FlowCard({ msg }) {
  const label = CATEGORY_LABELS[msg.category] || msg.category
  const isQuarantined = msg.status === 'quarantined'
  const isEncrypted = msg.encrypted

  return (
    <div className="flow-card" style={{
      border: `1px solid ${isQuarantined ? 'var(--sith)' : 'var(--line)'}`,
      background: 'var(--paper-elev)', borderRadius: 12, padding: 16, marginBottom: 12,
    }}>
      <div className="flow-card-header" style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10,
      }}>
        <div>
          <div style={{ fontSize: 12, color: 'var(--muted)' }}>
            {msg.channel === 'intergalactic_whatsapp' ? '\uD83D\uDCAC Intergalactic WhatsApp' : '\u2709\uFE0F Hologram Email'}
            {' \u2022 '}
            {new Date(msg.timestamp || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
          <div style={{ fontWeight: 700, fontSize: 15, marginTop: 2, color: 'var(--ink)' }}>{msg.sender}</div>
        </div>
        <div style={{
          padding: '3px 10px', borderRadius: 4, fontSize: 11, fontWeight: 700, whiteSpace: 'nowrap',
          ...(isQuarantined ? { background: 'var(--amber-soft)', color: '#c8775c' }
            : isEncrypted ? { background: 'var(--amber-soft)', color: '#8e6f1f' }
            : msg.status === 'completed' ? { background: '#e3f0e3', color: '#2d6b3f' }
            : msg.status === 'error' ? { background: '#f6e4dd', color: '#c8775c' }
            : msg.status === 'security_review' ? { background: 'var(--amber-soft)', color: '#8e6f1f' }
            : { background: '#e3ebf2', color: '#3a6a8a' }),
        }}>
          {isQuarantined ? '\u26D4 QUARANTINED'
            : isEncrypted ? '\uD83D\uDD12 ENCRYPTED'
            : msg.status === 'error' ? '\u26A0 ERROR'
            : msg.status === 'security_review' ? '\u2753 REVIEW'
            : msg.status.toUpperCase()}
        </div>
      </div>

      <div style={{ fontSize: 13, color: 'var(--ink-soft)', lineHeight: 1.5, marginBottom: 10, padding: '8px 10px', background: 'var(--paper-deep)', borderRadius: 4 }}>
        {isEncrypted ? '[Encrypted Yoda Strategy - Content Hidden]' : (msg.content && msg.content.length > 200 ? msg.content.slice(0, 200) + '...' : msg.content)}
      </div>

      {isQuarantined && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 10px', background: 'var(--amber-soft)', borderRadius: 4, color: '#c8775c', fontSize: 12 }}>
          <span style={{ fontSize: 18, fontWeight: 700 }}>{'\u26D4'}</span>
          <div>
            <div style={{ fontWeight: 700 }}>Security Threat Blocked</div>
            <div style={{ color: '#c8775c', marginTop: 2 }}>{msg.error || 'High-risk content detected'}</div>
            {msg.dark_side_indicators?.length > 0 && (
              <div style={{ color: 'var(--muted)', marginTop: 2 }}>Indicators: {msg.dark_side_indicators.join(', ')}</div>
            )}
          </div>
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
      .then((data) => setMessages(data.data || data))
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
        <p style={{ color: 'var(--muted)', fontSize: 13, marginBottom: 20 }}>
          See every request processed by the Rebellion today.
        </p>

        <div className="stats-grid" style={{ marginBottom: 20 }}>
          <div className="card"><h3>Total Requests</h3><div className="value">{messages.length}</div></div>
          <div className="card"><h3>Completed</h3><div className="value" style={{ color: 'var(--jedi)' }}>{completed.length}</div></div>
          <div className="card"><h3>{'\u26D4'} Threats Blocked</h3><div className="value" style={{ color: 'var(--sith)' }}>{quarantined.length}</div></div>
          <div className="card"><h3>{'\uD83D\uDD12'} Encrypted</h3><div className="value" style={{ color: 'var(--rebel)' }}>{encrypted.length}</div></div>
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
              <div className="card" style={{ textAlign: 'center', color: 'var(--muted)', padding: 40 }}>
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
              <div style={{ color: 'var(--jedi)', fontSize: 13 }}>{'\u2705'} No items require your decision right now.</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {leiaItems.map(m => (
                  <div key={m.id} style={{ padding: '8px 10px', background: 'var(--paper-elev)', border: '1px solid var(--line)', borderRadius: 12 }}>
                    <div style={{ fontWeight: 600, fontSize: 13, color: 'var(--ink)' }}>{m.sender}</div>
                    <div style={{ color: 'var(--muted)', fontSize: 11, marginTop: 2 }}>
                      {CATEGORY_LABELS[m.category] || m.category}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
