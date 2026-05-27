import React, { useEffect, useRef, useState } from 'react'
import { api } from '../api.js'
import './MorningBriefing.css'


function getInitials(name) {
  return name.split(/\s+/).map(w => w[0]).join('').slice(0, 2).toUpperCase()
}

function getInitialBg(name) {
  const colors = ['#1f2937', '#0ea5e9', '#dc2626', '#475569', '#7c3aed', '#f97316', '#10b981', '#a855f7']
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return colors[Math.abs(hash) % colors.length]
}

export default function MorningBriefing() {
  const [data, setData] = useState(null)
  const [messages, setMessages] = useState([])
  const [integrations, setIntegrations] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedId, setExpandedId] = useState(null)
  const toastBoxRef = useRef(null)
  const intervalRef = useRef(null)

  const load = () => {
    api.inbox().then(d => {
      setData(d)
      setLoading(false)
    }).catch(() => {
      if (!data) setError('Failed to load briefing')
      setLoading(false)
    })
    api.messages().then((data) => setMessages(data.data || data)).catch(() => {})
    api.integrations().then(setIntegrations).catch(() => {})
  }

  useEffect(() => {
    load()
    intervalRef.current = setInterval(load, 30000)
    return () => clearInterval(intervalRef.current)
  }, [])

  const toast = (opts) => {
    const { kind = '', title = '', body = '' } = opts
    const node = document.createElement('div')
    node.className = `toast ${kind}`
    const tDiv = document.createElement('div'); tDiv.className = 't-title'; tDiv.textContent = title
    const bDiv = document.createElement('div'); bDiv.className = 't-body'; bDiv.textContent = body
    node.append(tDiv, bDiv)
    toastBoxRef.current?.appendChild(node)
    setTimeout(() => { node.classList.add('fade'); setTimeout(() => node.remove(), 280) }, 4200)
  }

  if (error) return <div className="briefing-wrap"><div style={{padding: 40, textAlign: 'center', color: 'var(--sith)'}}>{error}</div></div>
  if (loading) return <div className="briefing-wrap"><div style={{padding: 40, textAlign: 'center', color: 'var(--muted-2)'}}>Generating briefing...</div></div>
  if (!data) return null

  const now = new Date()
  const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  const dateStr = now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })
  const firstItem = data.needs_attention?.[0]

  const channelIcon = (ch) => ch === 'intergalactic_whatsapp' ? '\uD83D\uDCAC' : '\u2709\uFE0F';
  const channelLabel = (ch) => ch === 'intergalactic_whatsapp' ? 'WhatsApp' : 'Hologram Email';
  const statusBadgeClass = (status) =>
    status === 'completed' ? 'completed'
    : status === 'quarantined' ? 'quarantined'
    : status === 'error' ? 'error'
    : 'pending';

  return (
    <div className="briefing-wrap">

      <header className="b-header">
        <div className="masthead">
          <img src="/logo.png" alt="Rebel Ops" style={{ height: 36, marginRight: 14, verticalAlign: 'middle', background: 'transparent' }} />
          <div className="word">
            <span>The Morning Report</span>
            <span className="rebel">— from your EA</span>
          </div>
          <div className="small" style={{ marginTop: 2, marginLeft: 50 }}>Daily Briefing · Rebel Command</div>
        </div>
        <div className="h-right">
          <span className="pill-soft"><span className="dot"></span>{data.total_messages} requests today</span>
          <button className="icon-btn ghost" onClick={() => toast({ title: 'Briefing refreshed', body: `Last updated ${timeStr}` })}>
            <svg viewBox="0 0 16 16" fill="none"><path d="M14 8a6 6 0 1 1-1.76-4.24M14 3v3.5h-3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
            Refresh
          </button>
        </div>
      </header>

      <div className="b-main">
        <div>
          <div className="b-greeting">
            <div className="pretitle">{dateStr} · {timeStr}</div>
            <h1>Good morning, <em>General Leia.</em></h1>
            <div className="stats-grid" style={{marginTop: 20, marginBottom: 6}}>
              <div className="stat-card">
                <div className="num" style={{color: 'var(--muted)'}}>{data.total_messages}</div>
                <div className="lbl">Total requests</div>
              </div>
              <div className="stat-card">
                <div className="num" style={{color: 'var(--jedi)'}}>{data.completed}</div>
                <div className="lbl">Completed</div>
              </div>
              <div className="stat-card">
                <div className="num" style={{color: 'var(--sith)'}}>{data.quarantined}</div>
                <div className="lbl">Threats blocked</div>
              </div>
              <div className="stat-card">
                <div className="num" style={{color: 'var(--rebel)'}}>{data.encrypted}</div>
                <div className="lbl">Encrypted</div>
              </div>
            </div>
          </div>

          <div className="wins">
            <div className="wins-title">Today, quietly:</div>
            <div className="wins-list">
              <div className="win"><span className="checkmark">✓</span><span className="text">All pipeline systems operational. No anomalies detected.</span></div>
              <div className="win"><span className="checkmark">✓</span><span className="text">{data.needs_attention?.length > 0 ? `${data.needs_attention.length} items await your review.` : 'All requests have been processed.'}</span></div>
              <div className="win"><span className="checkmark">✓</span><span className="text">{data.open_tasks?.length > 0 ? `${data.open_tasks.length} active tasks across the Rebellion.` : 'No outstanding tasks.'}</span></div>
            </div>
          </div>

          {data.needs_attention?.length > 0 && (
            <section className="b-block">
              <div className="head">
                <h2><span className="ord">i.</span>Requests needing your decision</h2>
                <span className="meta">{data.needs_attention.length} items</span>
              </div>
              <div className="attention-list">
                {data.needs_attention.map((item) => (
                  <div key={item.id}
                    className={`attention-item priority-${item.priority}`}
                    onClick={() => setExpandedId(expandedId === item.id ? null : item.id)}>
                    <span className="attention-av" style={{background: getInitialBg(item.sender)}}>{getInitials(item.sender)}</span>
                    <div>
                      <div className="attention-header">
                        <span className="attention-channel">{channelIcon(item.channel)} {channelLabel(item.channel)}</span>
                        <span className="attention-meta">{item.sender} · {item.category.replace(/_/g, ' ')}</span>
                      </div>
                      <div className="attention-subject">{item.subject.slice(0, 100)}</div>
                    </div>
                    <div style={{display: 'flex', flexDirection: 'column', gap: 4, alignItems: 'flex-end'}}>
                      <span className={`attention-tag ${item.priority === 'critical' ? 'urgent' : item.priority === 'high' ? 'high' : 'normal'}`}>
                        {item.priority}
                      </span>
                      {item.encrypted && <span className="st-badge encrypted">ENCRYPTED</span>}
                      {item.status === 'quarantined' && <span className="st-badge quarantined">BLOCKED</span>}
                    </div>
                    {expandedId === item.id && (
                      <div style={{
                        gridColumn: '1 / -1',
                        marginTop: 12,
                        paddingTop: 12,
                        borderTop: '1px solid var(--hairline)',
                        fontSize: 13,
                        color: 'var(--ink-soft)',
                        lineHeight: 1.5,
                      }}>
                        {item.encrypted ? (
                          <div style={{color: 'var(--rebel)', fontWeight: 600, fontSize: 12, marginTop: 8}}>Encrypted Yoda Strategy — Content Hidden</div>
                        ) : item.content ? (
                          <div style={{marginTop: 8, padding: '10px 12px', background: 'var(--paper-deep)', borderRadius: 6, fontSize: 13, lineHeight: 1.6}}>{item.content}</div>
                        ) : null}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}


        </div>

        <aside className="b-sidebar">
          {firstItem && (
            <div className="first-thing">
              <div className="label">Your first action today</div>
              <h3>{firstItem.sender} — {firstItem.category.replace(/_/g, ' ')}</h3>
              <p>{firstItem.subject.slice(0, 120)}</p>
              <div className="actions">
                <button className="a-btn primary" onClick={() => toast({ title: 'Action noted', body: `Marked ${firstItem.sender} as reviewed. Opening details...` })}>Review now</button>
                <button className="a-btn" onClick={() => toast({ title: 'Snoozed', body: 'This item will reappear in the next briefing.' })}>Snooze</button>
              </div>
            </div>
          )}

          <div className="side-card">
            <h4>{'\uD83D\uDCCB'} Today's delegation{messages.length > 0 ? ` (${messages.length} total)` : ''}</h4>
            {messages.length > 0 ? (
              (() => {
                const counts = {}
                messages.forEach(m => {
                  const owner = m.owner || (m.status === 'quarantined' ? 'Quarantined' : 'Unassigned')
                  counts[owner] = (counts[owner] || 0) + 1
                })
                return Object.entries(counts).sort((a, b) => b[1] - a[1]).map(([owner, count]) => (
                  <div key={owner} className="del-row">
                    <span>{owner}</span>
                    <span className="del-count">{count}</span>
                  </div>
                ))
              })()
            ) : (
              <div style={{ fontSize: 12, color: 'var(--muted)', padding: '6px 0' }}>
                No messages delegated yet.
              </div>
            )}
          </div>

          <div className="side-card">
            <h4>Quick actions</h4>
            <div className="quick-action" onClick={() => toast({ title: 'Briefing drafted', body: 'Next week\'s priorities ready for review.' })}>
              <span>✦ Generate weekly plan</span><span className="arr">→</span>
            </div>
            <div className="quick-action" onClick={async () => { try { await api.demoLoad(); load(); toast({ title: 'Demo loaded', body: '16 demo messages processed through the pipeline.' }) } catch { toast({ title: 'Demo failed', body: 'Could not load demo messages.' }) } }}>
              <span>Run demo scenario</span><span className="arr">→</span>
            </div>
            <div className="quick-action" onClick={async () => { try { await api.generateBriefing(); toast({ title: 'Report sent', body: 'Daily briefing delivered to your inbox.' }) } catch { toast({ title: 'Send failed', body: 'Could not email the briefing.' }) } }}>
              <span>Email me this briefing</span><span className="arr">→</span>
            </div>
          </div>

          {data.schedule?.length > 0 && (
            <div className="side-card side-calendar">
              <h4>{'\uD83D\uDCC5'} Today's calendar</h4>
              <div className="schedule">
                {data.schedule.map((s, i) => (
                  <div key={i} className="sched-row">
                    <div className="time">{s.time}</div>
                    <div className="dot"></div>
                    <div>
                      <div className="title">{s.subject.slice(0, 50)}</div>
                      <div className="desc">{s.requestor}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="side-card">
            <h4>Connected sources</h4>
            {integrations ? (
              [["gmail","Gmail"],["calendar","Calendar"],["clickup","ClickUp"],["whatsapp","WhatsApp"],["discord","Discord"],].map(([key, label]) => (
                <div key={key} className="source-row">
                  <span><span className="status-dot" style={{background: integrations[key] ? '#10b981' : '#8e8e88'}}></span>{label}</span>
                  <span className={integrations[key] ? 'live' : 'off'}>{integrations[key] ? 'live' : 'mock'}</span>
                </div>
              ))
            ) : (
              <div style={{fontSize:12,color:'var(--muted)',padding:'6px 0'}}>Loading...</div>
            )}
          </div>
        </aside>
      </div>

      <div className="toast-box" ref={toastBoxRef}></div>
    </div>
  )
}

