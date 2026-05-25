import React, { useState } from 'react'
import './Architecture.css'

const NODES = [
  {
    id: 'intake', label: 'Request Intake',
    icon: '\uD83D\uDCE5',
    subtitle: 'WhatsApp \u2022 Hologram Email',
    detail: 'All incoming requests arrive through Intergalactic WhatsApp or Hologram Email. The IntakeAgent validates sender, content length, and assigns a unique ID.',
    outputs: [{ to: 'security', label: 'all messages' }],
  },
  {
    id: 'security', label: 'Security Scan',
    icon: '\uD83D\uDEE1\uFE0F',
    subtitle: 'DarkSideSecurityAgent',
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
    detail: 'The message is blocked immediately. No information is shared. Security Team is notified. An investigation task is created via ErrorProtocolAgent.',
    terminal: true,
  },
  {
    id: 'classifier', label: 'AI Classifier',
    icon: '\uD83E\uDD16',
    subtitle: 'C-3PO Categorizes',
    detail: 'C-3PO classifies into 15 categories: calendar_booking, planet_help, recruitment, logistics, urgent_security, jedi_training_diplomacy, ahsoka_special_mission, yoda_encrypted_strategy, and more. Sets priority, Jedi case type, and flags if Leia is needed.',
    outputs: [{ to: 'router', label: 'category assigned' }],
  },
  {
    id: 'router', label: 'Routing Engine',
    icon: '\uD83D\uDD01',
    subtitle: 'Assigns Owner + Team',
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
    detail: 'Calendar bookings and items requiring Leia go here. Leia only sees high-value decisions, VIP meetings, and final escalations.',
  },
  {
    id: 'defense', label: 'Rebel Defense Team',
    icon: '\uD83C\uDF96\uFE0F',
    subtitle: 'Planet Help & Defense',
    detail: 'Handles planetary aid requests, crisis response, and defense coordination. Creates a task and dispatches support.',
  },
  {
    id: 'solo', label: 'Han Solo',
    icon: '\uD83D\uDE80',
    subtitle: 'Logistics Team',
    detail: 'Handles supply delivery, transport, fuel credits, and cargo routing. Creates a logistics task.',
  },
  {
    id: 'yoda', label: 'Master Yoda',
    icon: '\uD83E\uDDD9',
    subtitle: 'Jedi Council',
    detail: 'Only receives encrypted strategic transmissions. Messages are encrypted via YodaEncryptionAgent and stored as EncryptedTransmission records.',
    outputs: [{ to: 'encrypt', label: 'encrypt & store' }],
  },
  {
    id: 'encrypt', label: 'Encryption',
    icon: '\uD83D\uDD10',
    subtitle: 'YodaEncryptionAgent',
    detail: 'The message content is encrypted (demo: reverse-string cipher). An EncryptedTransmission record is created with ciphertext and method metadata.',
    terminal: true,
  },
  {
    id: 'ahsoka', label: 'Ahsoka Tano',
    icon: '\uD83D\uDD75\uFE0F',
    subtitle: 'Special Mission Review',
    detail: 'Complex situations needing judgment before escalation. Ahsoka assesses whether the contact is an ally, monitored contact, or risk.',
  },
  {
    id: 'djarin', label: 'Din Djarin',
    icon: '\uD83D\uDEE1\uFE0F',
    subtitle: 'Protection Team',
    detail: 'Protection missions, informant extraction, confidential transport. Marked restricted. Security level set to high.',
  },
  {
    id: 'r2', label: 'R2-D2',
    icon: '\uD83E\uDDF0',
    subtitle: 'Operations Analytics',
    detail: 'Data support requests: status reports, data lookups, coordinate retrieval, and analysis summaries.',
  },
  {
    id: 'organizations', label: 'Other Teams',
    icon: '\uD83D\uDC65',
    subtitle: '6 more owners available',
    detail: 'Recruitment -> Rebel Recruitment Team. Soldier Support -> Operations. Training -> Luke+Ben. Partnerships -> Partnerships Team. Urgent Security -> Security Team (BB-8 alert). Field Operations -> Chewbacca.',
    outputs: [{ to: 'briefing', label: 'all reports' }],
  },
  {
    id: 'calendar', label: 'Calendar',
    icon: '\uD83D\uDCC5',
    subtitle: 'Availability Check',
    detail: 'Checks availability and suggests time slots. Private Leia events are stored internally but never exposed via the public API.',
    outputs: [{ to: 'briefing', label: 'bookings' }],
  },
  {
    id: 'briefing', label: 'Daily Briefing',
    icon: '\uD83D\uDCCA',
    subtitle: 'ReportingAgent',
    detail: 'Generates the Daily Hologram Briefing for General Leia. Includes: total requests, category breakdown, owner breakdown, critical items, security risks, blocked items, decisions needed, and recommended focus.',
    terminal: true,
  },
]

const PHASES = [
  {
    id: 'ingestion',
    icon: '\uD83D\uDCE5',
    label: 'Ingestion',
    subtitle: 'Request Intake',
    desc: 'Messages enter the pipeline via Intergalactic WhatsApp or Hologram Email. Each request gets a unique ID and is validated.',
    nodes: ['intake'],
  },
  {
    id: 'security',
    icon: '\uD83D\uDEE1\uFE0F',
    label: 'Security Scan',
    subtitle: 'Dark Side Detection',
    desc: 'Every message is scanned for Dark Side threats. Safe messages proceed to classification; threats are quarantined immediately.',
    nodes: ['security', 'quarantine'],
  },
  {
    id: 'classify',
    icon: '\uD83E\uDD16',
    label: 'Classification',
    subtitle: 'C-3PO AI Classification',
    desc: 'C-3PO classifies each request into one of 15 categories, sets priority, and flags items needing General Leia.',
    nodes: ['classifier'],
  },
  {
    id: 'routing',
    icon: '\uD83D\uDD01',
    label: 'Routing Engine',
    subtitle: 'Owner & Team Assignment',
    desc: 'Each category is routed to the correct owner or team. A Task record is created for every routed request.',
    nodes: ['router'],
    showOwners: true,
  },
  {
    id: 'delivery',
    icon: '\uD83D\uDCE8',
    label: 'Delivery',
    subtitle: 'Final Processing & Reporting',
    desc: 'Results are delivered through calendar bookings, encrypted storage, or the daily briefing for General Leia.',
    nodes: ['calendar', 'encrypt', 'briefing'],
  },
]

const OWNER_MAP = [
  { id: 'leia', name: 'General Leia', icon: '\uD83D\uDC69\u200D\u2708\uFE0F', category: 'calendar_booking' },
  { id: 'defense', name: 'Rebel Defense Team', icon: '\uD83C\uDF96\uFE0F', category: 'planet_help' },
  { id: 'solo', name: 'Han Solo', icon: '\uD83D\uDE80', category: 'logistics' },
  { id: 'yoda', name: 'Master Yoda', icon: '\uD83E\uDDD9', category: 'yoda_encrypted_strategy' },
  { id: 'ahsoka', name: 'Ahsoka Tano', icon: '\uD83D\uDD75\uFE0F', category: 'ahsoka_special_mission' },
  { id: 'djarin', name: 'Din Djarin', icon: '\uD83D\uDEE1\uFE0F', category: 'special_protection' },
  { id: 'r2', name: 'R2-D2', icon: '\uD83E\uDDF0', category: 'data_support' },
  { id: 'organizations', name: 'Other Teams', icon: '\uD83D\uDC65', category: 'other' },
]

const NODE_ICONS = {
  leia: '/icons/Leia.png',
  solo: '/icons/Han Solo.png',
  yoda: '/icons/Yoda.png',
  djarin: '/icons/Din Djarin.png',
  r2: '/icons/R2D2.png',
  quarantine: '/icons/Quarentene.png',
  classifier: '/icons/C3PO.png',
}

const OWNER_ICONS = {
  leia: '/icons/Leia.png',
  solo: '/icons/Han Solo.png',
  yoda: '/icons/Yoda.png',
  djarin: '/icons/Din Djarin.png',
  r2: '/icons/R2D2.png',
}

function catLabel(cat) {
  return cat.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

export default function WorkflowGraph() {
  const [expanded, setExpanded] = useState({ ingestion: true })
  const [selectedNode, setSelectedNode] = useState(null)

  const togglePhase = (id) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  const handleNodeClick = (nodeId) => {
    setSelectedNode((prev) => (prev === nodeId ? null : nodeId))
  }

  const getNode = (id) => NODES.find((n) => n.id === id)

  const renderNodeCard = (id) => {
    const node = getNode(id)
    if (!node) return null
    const sel = selectedNode === id
    return (
      <div
        key={id}
        className={`arch-node ${sel ? 'selected' : ''} ${node.terminal ? 'terminal' : ''}`}
        onClick={() => handleNodeClick(id)}
      >
        <div className="arch-node-main">
          <span className="arch-node-icon">
            {NODE_ICONS[node.id]
              ? <img src={NODE_ICONS[node.id]} alt={node.label} className="icon-img-sm" />
              : node.icon}
          </span>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="arch-node-label">{node.label}</div>
            <div className="arch-node-sub">{node.subtitle}</div>
          </div>
          {node.terminal && <span className="arch-terminal-badge">ENDPOINT</span>}
        </div>
        {node.outputs && !sel && (
          <div className="arch-node-outputs">
            {node.outputs.map((o, i) => (
              <span key={i} className="arch-output-tag">{'\u2192'} {o.label}</span>
            ))}
          </div>
        )}
        {sel && (
          <div className="arch-node-detail">
            <p>{node.detail}</p>
            {node.outputs && (
              <div className="arch-detail-outputs">
                {node.outputs.map((o, i) => (
                  <span key={i} className="arch-detail-output">
                    {'\u2192'} {o.label} <span className="arch-dest">{o.to}</span>
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    )
  }

  const renderPhase = (phase, idx) => {
    const isOpen = expanded[phase.id]

    let body = null
    if (isOpen) {
      body = (
        <div className="arch-phase-body">
          <div className="arch-phase-desc">{phase.desc}</div>

          <div className="arch-nodes">
            {phase.nodes.map(renderNodeCard)}
          </div>

          {phase.id === 'security' && (
            <div className="arch-branch">
              <div className="arch-branch-path safe">
                <div>
                  <span className="branch-icon">{'\u2705'}</span>
                  <span className="branch-label">Safe — Risk &lt; 50</span>
                </div>
                <span className="branch-dest">{'\u2192'} Proceeds to Classification (Phase 3)</span>
              </div>
              <div className="arch-branch-path threat">
                <div>
                  <span className="branch-icon">{'\u26D4'}</span>
                  <span className="branch-label">Threat — Risk &ge; 50</span>
                </div>
                <span className="branch-dest">{'\u2192'} Blocked · Quarantine (endpoint)</span>
              </div>
            </div>
          )}

          {phase.showOwners && (
            <div style={{ marginTop: 14 }}>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: 8 }}>
                {'\uD83D\uDCCD'} Routing destinations
              </div>
              <div className="arch-owner-grid">
                {OWNER_MAP.map((o) => {
                  const isOwnerSelected = selectedNode === o.id
                  return (
                    <div
                      key={o.id}
                      className={`arch-owner-item ${isOwnerSelected ? 'selected' : ''}`}
                      onClick={() => handleNodeClick(o.id)}
                    >
                      <span className="oi-icon">
                        {OWNER_ICONS[o.id]
                          ? <img src={OWNER_ICONS[o.id]} alt={o.name} className="icon-img-sm" />
                          : o.icon}
                      </span>
                      <div>
                        <div className="oi-name">{o.name}</div>
                        <span className="oi-cat">{catLabel(o.category)}</span>
                      </div>
                    </div>
                  )
                })}
              </div>
              {OWNER_MAP.some((o) => selectedNode === o.id) && (
                <div className="arch-owner-detail">
                  {(() => {
                    const owner = OWNER_MAP.find((o) => o.id === selectedNode)
                    const node = getNode(owner.id)
                    return <p>{node ? node.detail : ''}</p>
                  })()}
                </div>
              )}
            </div>
          )}
        </div>
      )
    }

    return (
      <div key={phase.id} className="arch-phase" style={phase.id === 'security' ? { borderLeft: '3px solid var(--sith)' } : phase.id === 'routing' ? { borderLeft: '3px solid var(--rebel)' } : {}}>
        <div className="arch-phase-header" onClick={() => togglePhase(phase.id)}>
          <span className="ph-icon">{phase.icon}</span>
          <div className="ph-info">
            <div className="ph-label">{phase.label}</div>
            <div className="ph-subtitle">{phase.subtitle}</div>
          </div>
          <span className={`ph-toggle ${isOpen ? 'open' : ''}`}>{'\u25BC'}</span>
        </div>
        {body}
      </div>
    )
  }

  return (
    <div className="arch-container">
      <div className="arch-header">
        <h2>System Architecture</h2>
        <p>
          Click any component to learn how the Rebellion&apos;s message processing pipeline works.
          The pipeline has {PHASES.length} phases and {NODES.length} components.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
        {PHASES.map((phase, idx) => (
          <div key={phase.id}>
            {renderPhase(phase, idx)}
            {idx < PHASES.length - 1 && (
              <div className="arch-flow-arrow">{'\u2193'}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
