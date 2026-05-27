import React, { useEffect, useState } from 'react'
import { api } from '../api.js'

const ICON_FILES = {
  'General Leia': '/icons/Leia.png',
  'C-3PO': '/icons/C3PO.png',
  'Yoda': '/icons/Yoda.png',
  'Luke + Ben Kenobi': '/icons/Obi Wan.png',
  'R2-D2': '/icons/R2D2.png',
  'BB-8': '/icons/BB8.png',
  'Han Solo': '/icons/Han Solo.png',
  'Chewbacca': '/icons/Chewbaca.png',
  'Grogu Care Team': '/icons/Grogu.png',
  'Ahsoka Tano': '/icons/Ahsoka Tano.png',
  'Din Djarin': '/icons/Din Djarin.png',
  'Operations Team': '/icons/Operations.png',
  'Logistics Team': '/icons/Logistics.png',
}

const OWNERS = [
  { name: 'General Leia', icon: '\uD83D\uDC78', role: 'Executive decision-maker. Handles VIP meetings, final approvals, major escalations, and high-value decisions.', business: 'Entrepreneur, CEO, founder, or executive whose time must be protected.' },
  { name: 'C-3PO', icon: '\uD83E\uDD16', role: 'AI classifier. Reads, summarizes, classifies, and routes incoming requests.', business: 'AI executive assistant, intake coordinator, or operations assistant.' },
  { name: 'Yoda', icon: '\uD83E\uDDD9', role: 'Encrypted strategic advisor. Receives encrypted strategic questions only.', business: 'Board advisor, investor advisor, legal advisor, senior strategist, or executive mentor.' },
  { name: 'Luke + Ben Kenobi', icon: '\uD83D\uDD2E', role: 'Jedi Training & Diplomacy Team. Handles training, diplomacy, mediation, mentoring, and leadership support.', business: 'Training team, enablement team, leadership coach, HR support, customer success, or conflict-resolution team.' },
  { name: 'Ahsoka Tano', icon: '\uD83D\uDD75\uFE0F', role: 'Special Mission Review. Handles complex situations where judgment is needed before escalation.', business: 'Chief of staff, special projects leader, crisis advisor, senior operator, or independent reviewer.' },
  { name: 'R2-D2', icon: '\uD83E\uDDF0', role: 'Data and reporting. Retrieves records, checks status, and prepares summaries.', business: 'Operations analyst, business intelligence assistant, reporting automation, or systems administrator.' },
  { name: 'BB-8', icon: '\u26A1', role: 'Fast alerts. Sends urgent escalation messages and critical updates.', business: 'Real-time alert system, incident notification assistant, or urgent escalation workflow.' },
  { name: 'Han Solo', icon: '\uD83D\uDE9A', role: 'Logistics and transport. Handles delivery, supplies, resource movement, and urgent logistics.', business: 'Logistics manager, procurement lead, vendor coordinator, fulfillment owner, or supply chain operator.' },
  { name: 'Chewbacca', icon: '\uD83D\uDC4A', role: 'Field operations. Handles repairs, field support, hands-on problems, and operational execution.', business: 'Field operations team, implementation specialist, technical support, facilities support, or crisis execution team.' },
  { name: 'Grogu Care Team', icon: '\uD83D\uDC76', role: 'Sensitive Force-related or vulnerable cases.', business: 'Sensitive client care, VIP support, confidential HR cases, high-potential talent program, or special-care escalation.' },
  { name: 'Din Djarin', icon: '\uD83D\uDEE1\uFE0F', role: 'Protection, extraction, confidential transport, and high-risk missions.', business: 'Security lead, executive protection, high-risk project owner, confidential operations, or crisis response.' },
  { name: 'Jedi Council', icon: '\uD83D\uDCAD', role: 'Ethical, sensitive, or high-impact reviews.', business: 'Advisory board, executive committee, compliance committee, ethics committee, or leadership review board.' },
  { name: 'Rebel Defense Team', icon: '\uD83C\uDF0D', role: 'Planets under threat and defense coordination.', business: 'Client escalation team, emergency response team, crisis operations, or service delivery.' },
  { name: 'Rebel Recruitment Team', icon: '\uD83E\uDD4D', role: 'People who want to join the Rebellion.', business: 'Recruiting, HR, talent acquisition, contractor onboarding, or volunteer coordination.' },
  { name: 'Operations Team', icon: '\uD83D\uDEE0\uFE0F', role: 'Internal soldier support and general operational needs.', business: 'Admin operations, employee support, back office, or internal ops.' },
  { name: 'Training Team', icon: '\uD83C\uDF93', role: 'Civilian training and preparedness.', business: 'Customer education, employee onboarding, enablement, learning and development.' },
  { name: 'Logistics Team', icon: '\uD83D\uDE82', role: 'Resources, supplies, transport, and delivery.', business: 'Procurement, supply chain, inventory, fulfillment, and vendor management.' },
  { name: 'Security Team', icon: '\uD83D\uDD12', role: 'Dark Side threat detection and suspicious requests.', business: 'Cybersecurity, compliance, fraud prevention, legal review, and information security.' },
  { name: 'Partnerships Team', icon: '\uD83E\uDD1D', role: 'Allies, senators, donors, and strategic supporters.', business: 'Business development, partnerships, investor relations, sponsorships, and strategic alliances.' },
]

export default function Owners() {
  const [data, setData] = useState(null)

  useEffect(() => {
    api.inbox().then(setData).catch(() => {})
  }, [])

  const delegation = data?.delegation || {}

  return (
    <div className="owners-page">
      <div className="page-header">
        <h2>Team Directory</h2>
        <p>Workflow roles and their business meaning</p>
      </div>

      <div className="quote-card">
        <p>Automation does not replace the entrepreneur. It protects the entrepreneur&apos;s time. The entrepreneur should only handle high-value decisions, VIP meetings, and final escalations.</p>
      </div>

      <div className="owner-grid">
        {OWNERS.map((o) => (
          <div key={o.name} className="owner-card card">
            <div className="owner-header">
              <span className="owner-icon">
                {ICON_FILES[o.name]
                  ? <img src={ICON_FILES[o.name]} alt={o.name} className="icon-img" />
                  : o.icon}
              </span>
              <h3>{o.name}</h3>
              {delegation[o.name] && (
                <span className="badge badge-count">{delegation[o.name]} tasks</span>
              )}
            </div>
            <div className="owner-section">
              <div className="owner-label">Workflow Role</div>
              <div className="owner-value">{o.role}</div>
            </div>
            <div className="owner-section">
              <div className="owner-label">Business Meaning</div>
              <div className="owner-value business">{o.business}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="card" style={{ marginTop: 24, padding: 20 }}>
        <h3 style={{ margin: '0 0 12px', fontSize: 15, color: 'var(--ink)' }}>How It Works</h3>
        <p style={{ fontSize: 13, color: 'var(--ink-soft)', lineHeight: 1.6, margin: 0 }}>
          Every request that arrives through Intergalactic WhatsApp or Hologram Email is scanned
          for Dark Side threats, classified by C-3PO, and routed to the right owner or team.
          Each owner represents a business function — from executive decisions to field operations.
          The system protects General Leia&apos;s time by only surfacing the highest-value decisions.
        </p>
      </div>
    </div>
  )
}