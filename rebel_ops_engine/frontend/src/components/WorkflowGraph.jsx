import React, { useState } from 'react'

const PIPELINE = [
  {
    id: 'intake', label: 'Request Intake',
    icon: '\uD83D\uDCE5',
    subtitle: 'WhatsApp \u2022 Hologram Email',
    color: '#4fc3f7',
    detail: 'All incoming requests arrive through Intergalactic WhatsApp or Hologram Email. The IntakeAgent validates sender, content length, and assigns a unique ID.',
    outputs: [{ to: 'security', label: 'all messages' }],
  },
  {
    id: 'security', label: 'Security Scan',
    icon: '\uD83D\uDEE1\uFE0F',
    subtitle: 'DarkSideSecurityAgent',
    color: '#f44336',
    detail: 'Scans every message for Dark Side threats: Emperor Palpatine, Darth Vader, Sith, infiltration, secret Rebel base requests, Leia private schedule requests. High-risk is quarantined.',
    outputs: [
      { to: 'classifier', label: 'Safe (risk < 50)' },
      { to: 'quarantine', label: 'High Risk (risk >= 50)' },
    ],
  },
  {
    id: 'quarantine', label: 'Quarantine',
    icon: '\uD83D\uDD12',
    subtitle: 'Threat Blocked',
    color: '#ef5350',
    detail: 'The message is blocked immediately. No information is shared. Security Team is notified. An investigation task is created via ErrorProtocolAgent.',
    terminal: true,
  },
  {
    id: 'classifier', label: 'AI Classifier',
    icon: '\uD83E\uDD16',
    subtitle: 'C-3PO Categorizes',
    color: '#2196f3',
    detail: 'C-3PO classifies into 15 categories: calendar_booking, planet_help, recruitment, logistics, urgent_security, jedi_training_diplomacy, ahsoka_special_mission, yoda_encrypted_strategy, and more. Sets priority, Jedi case type, and flags if Leia is needed.',
    outputs: [{ to: 'router', label: 'category assigned' }],
  },
  {
    id: 'router', label: 'Routing Engine',
    icon: '\uD83D\uDD01',
    subtitle: 'Assigns Owner + Team',
    color: '#ff9800',
    detail: 'Each category routes to the correct owner. A Task record is created. Special cases: Force-sensitive children go to Grogu Care Team. Yoda strategy goes to encrypted channel.',
    outputs: [
      { to: 'leia', label: 'Calendar Booking' },
      { to: 'defense', label: 'Planet Help' },
      { to: 'solo', label: 'Logistics' },
      { to: 'yoda', label: 'Encrypted Strategy' },
      { to: 'ahsoka', label: 'Special Mission' },
      { to: 'djarin', label: 'Protection' },
      { to: 'r2', label: 'Data Support' },
      { to: 'organizations', label: 'Others...' },
    ],
  },
  {
    id: 'leia', label: 'General Leia',
    icon: '\uD83D\uDC69\u200D\u2708\uFE0F',
    subtitle: 'Executive Office',
    color: '#e91e63',
    detail: 'Calendar bookings and items requiring Leia go here. Leia only sees high-value decisions, VIP meetings, and final escalations.',
    outputs: [{ to: 'calendar', label: 'booking request' }, { to: 'briefing', label: 'daily report' }],
  },
  {
    id: 'defense', label: 'Rebel Defense Team',
    icon: '\uD83C\uDF96\uFE0F',
    subtitle: 'Planet Help & Defense',
    color: '#81c784',
    detail: 'Handles planetary aid requests, crisis response, and defense coordination. Creates a task and dispatches support.',
  },
  {
    id: 'solo', label: 'Han Solo',
    icon: '\uD83D\uDE80',
    subtitle: 'Logistics Team',
    color: '#64b5f6',
    detail: 'Handles supply delivery, transport, fuel credits, and cargo routing. Creates a logistics task.',
  },
  {
    id: 'yoda', label: 'Master Yoda',
    icon: '\uD83E\uDDD9',
    subtitle: 'Jedi Council',
    color: '#baa182',
    detail: 'Only receives encrypted strategic transmissions. Messages are encrypted via YodaEncryptionAgent and stored as EncryptedTransmission records.',
    outputs: [{ to: 'encrypt', label: 'encrypt & store' }],
  },
  {
    id: 'encrypt', label: 'Encryption',
    icon: '\uD83D\uDD10',
    subtitle: 'YodaEncryptionAgent',
    color: '#ffd54f',
    detail: 'The message content is encrypted (demo: reverse-string cipher). An EncryptedTransmission record is created with ciphertext and method metadata.',
    terminal: true,
  },
  {
    id: 'ahsoka', label: 'Ahsoka Tano',
    icon: '\uD83D\uDD75\uFE0F',
    subtitle: 'Special Mission Review',
    color: '#f06292',
    detail: 'Complex situations needing judgment before escalation. Ahsoka assesses whether the contact is an ally, monitored contact, or risk.',
  },
  {
    id: 'djarin', label: 'Din Djarin',
    icon: '\uD83D\uDEE1\uFE0F',
    subtitle: 'Protection Team',
    color: '#ff8a65',
    detail: 'Protection missions, informant extraction, confidential transport. Marked restricted. Security level set to high.',
  },
  {
    id: 'r2', label: 'R2-D2',
    icon: '\uD83E\uDD16',
    subtitle: 'Operations Analytics',
    color: '#a1887f',
    detail: 'Data support requests: status reports, data lookups, coordinate retrieval, and analysis summaries.',
  },
  {
    id: 'organizations', label: 'Other Teams',
    icon: '\uD83D\uDC65',
    subtitle: '6 more owners available',
    color: '#90a4ae',
    detail: 'Recruitment -> Rebel Recruitment Team. Soldier Support -> Operations. Training -> Luke+Ben. Partnerships -> Partnerships Team. Urgent Security -> Security Team (BB-8 alert). Field Operations -> Chewbacca.',
    outputs: [{ to: 'briefing', label: 'all reports' }],
  },
  {
    id: 'calendar', label: 'Calendar',
    icon: '\uD83D\uDCC5',
    subtitle: 'Availability Check',
    color: '#00bcd4',
    detail: 'Checks availability and suggests time slots. Private Leia events are stored internally but never exposed via the public API.',
    outputs: [{ to: 'briefing', label: 'bookings' }],
  },
  {
    id: 'briefing', label: 'Daily Briefing',
    icon: '\uD83D\uDCCA',
    subtitle: 'ReportingAgent',
    color: '#607d8b',
    detail: 'Generates the Daily Hologram Briefing for General Leia. Includes: total requests, category breakdown, owner breakdown, critical items, security risks, blocked items, decisions needed, and recommended focus.',
    terminal: true,
  },
]

const NODE_WIDTH = 180
const NODE_HEIGHT = 70

export default function WorkflowGraph() {
  const [selected, setSelected] = useState(null)
  const [hoveredEdge, setHoveredEdge] = useState(null)

  const getRow = (id) => {
    const positions = {
      intake: 0, security: 1, quarantine: 2, classifier: 2, router: 3,
      leia: 4, defense: 4, solo: 4, yoda: 4, ahsoka: 4, djarin: 4, r2: 4, organizations: 4,
      encrypt: 5, calendar: 5, briefing: 6,
    }
    return positions[id] || 0
  }

  const getCol = (id, row) => {
    const cols = {
      intake: { 0: 5 },
      security: { 1: 5 },
      quarantine: { 2: 8 },
      classifier: { 2: 2 },
      router: { 3: 5 },
      leia: { 4: 0 }, defense: { 4: 2 }, solo: { 4: 4 }, yoda: { 4: 6 }, ahsoka: { 4: 7 }, djarin: { 4: 8 }, r2: { 4: 9 }, organizations: { 4: 10 },
      encrypt: { 5: 6 }, calendar: { 5: 0 },
      briefing: { 6: 5 },
    }
    return (cols[id] && cols[id][row]) || 0
  }

  const COL_GAP = 200
  const ROW_GAP = 100

  const nodePos = {}
  PIPELINE.forEach((n) => {
    const row = getRow(n.id)
    const col = getCol(n.id, row)
    nodePos[n.id] = { row, col, x: col * COL_GAP + 40, y: row * ROW_GAP + 30 }
  })

  const svgWidth = 11 * COL_GAP + 80
  const svgHeight = 7 * ROW_GAP + 60

  const renderEdges = () => {
    const edges = []
    PIPELINE.forEach((n) => {
      if (!n.outputs) return
      n.outputs.forEach((out) => {
        const from = nodePos[n.id]
        const to = nodePos[out.to]
        if (!from || !to) return
        const x1 = from.x + NODE_WIDTH
        const y1 = from.y + NODE_HEIGHT / 2
        const x2 = to.x
        const y2 = to.y + NODE_HEIGHT / 2
        const midX = (x1 + x2) / 2
        const isHighlighted = hoveredEdge === `${n.id}->${out.to}`
        edges.push(
          <g key={`${n.id}->${out.to}`}>
            <path
              d={`M${x1},${y1} C${midX},${y1} ${midX},${y2} ${x2},${y2}`}
              fill="none"
              stroke={isHighlighted ? '#4fc3f7' : '#2a3346'}
              strokeWidth={isHighlighted ? 2.5 : 1.5}
              strokeDasharray={n.id === 'yoda' ? '6,3' : 'none'}
              onMouseEnter={() => setHoveredEdge(`${n.id}->${out.to}`)}
              onMouseLeave={() => setHoveredEdge(null)}
              style={{ cursor: 'pointer', transition: 'all 0.2s' }}
            />
            <rect
              x={midX - 55} y={y1 - 28} width={110} height={18} rx={4}
              fill={isHighlighted ? '#1a2740' : '#141a24'}
              stroke={isHighlighted ? '#4fc3f7' : '#2a3346'}
              strokeWidth={1}
              onMouseEnter={() => setHoveredEdge(`${n.id}->${out.to}`)}
              onMouseLeave={() => setHoveredEdge(null)}
              style={{ cursor: 'pointer' }}
            />
            <text
              x={midX} y={y1 - 16}
              textAnchor="middle"
              fill={isHighlighted ? '#4fc3f7' : '#8892a4'}
              fontSize={10}
              onMouseEnter={() => setHoveredEdge(`${n.id}->${out.to}`)}
              onMouseLeave={() => setHoveredEdge(null)}
              style={{ cursor: 'pointer' }}
            >
              {out.label}
            </text>
          </g>
        )
      })
    })
    return edges
  }

  return (
    <div>
      <h2 style={{ marginBottom: 4 }}>System Architecture</h2>
      <p style={{ color: '#8892a4', fontSize: 13, marginBottom: 16 }}>
        Click any node to learn how each component works. This is the full engine powering the Rebellion.
      </p>

      <div style={{
        overflowX: 'auto', overflowY: 'hidden',
        background: '#0f131e', border: '1px solid #2a3346', borderRadius: 8,
        padding: '10px 0',
      }}>
        <svg width={svgWidth} height={svgHeight} style={{ display: 'block', minWidth: svgWidth }}>
          {renderEdges()}
          {PIPELINE.map((n) => {
            const pos = nodePos[n.id]
            const isSelected = selected?.id === n.id
            return (
              <g
                key={n.id}
                onClick={() => setSelected(isSelected ? null : n)}
                style={{ cursor: 'pointer' }}
              >
                <rect
                  x={pos.x} y={pos.y} width={NODE_WIDTH} height={NODE_HEIGHT} rx={8}
                  fill={isSelected ? '#1a2740' : '#141a24'}
                  stroke={isSelected ? '#4fc3f7' : n.terminal ? '#ef5350' : n.color}
                  strokeWidth={isSelected ? 2 : 1}
                />
                <text x={pos.x + 14} y={pos.y + 24} fontSize={16}>{n.icon}</text>
                <text x={pos.x + 40} y={pos.y + 24} fill="#e0e0e0" fontSize={13} fontWeight={600}>
                  {n.label.length > 18 ? n.label.slice(0, 17) + '...' : n.label}
                </text>
                <text x={pos.x + 40} y={pos.y + 42} fill="#8892a4" fontSize={10}>
                  {n.subtitle.length > 28 ? n.subtitle.slice(0, 27) + '...' : n.subtitle}
                </text>
              </g>
            )
          })}
        </svg>
      </div>

      {selected && (
        <div className="card" style={{ marginTop: 16, border: `1px solid ${selected.color}` }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
            <span style={{ fontSize: 24 }}>{selected.icon}</span>
            <div>
              <div style={{ fontWeight: 700, fontSize: 16, color: '#f0f0f0' }}>{selected.label}</div>
              <div style={{ fontSize: 12, color: '#8892a4' }}>{selected.subtitle}</div>
            </div>
          </div>
          <p style={{ fontSize: 13, color: '#c8d6e5', lineHeight: 1.6 }}>{selected.detail}</p>
          {selected.outputs && (
            <div style={{ marginTop: 8, fontSize: 12, color: '#8892a4' }}>
              <strong>Outputs:</strong>{' '}
              {selected.outputs.map((o, i) => (
                <span key={i} style={{ color: '#4fc3f7' }}>
                  {i > 0 ? ', ' : ''}{o.label} {'\u2192'} {o.to}
                </span>
              ))}
            </div>
          )}
          {selected.terminal && (
            <div style={{ marginTop: 8, fontSize: 12, color: '#ef5350' }}>
              {'Endpoint \u2014 no further routing'}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
