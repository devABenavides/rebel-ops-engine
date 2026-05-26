import { http, HttpResponse } from 'msw'

const BASE = '/api'

const mockMessages = [
  { id: 'msg-1', channel: 'intergalactic_whatsapp', sender: 'Han Solo', content: 'Need fuel for Millennium Falcon', status: 'completed', category: 'logistics', owner: 'Han Solo', risk_score: 10, encrypted: false, timestamp: '2026-05-26T08:00:00Z', requires_leia: false },
  { id: 'msg-2', channel: 'hologram_email', sender: 'Darth Vader', content: 'I am your father', status: 'quarantined', category: 'urgent_security', owner: 'Security Team', risk_score: 95, encrypted: false, timestamp: '2026-05-26T08:05:00Z', requires_leia: false, dark_side_indicators: ['darth vader'], error: 'High-risk content detected' },
  { id: 'msg-3', channel: 'intergalactic_whatsapp', sender: 'Yoda', content: 'Encrypted strategy for the rebellion', status: 'completed', category: 'yoda_encrypted_strategy', owner: 'Yoda', risk_score: 5, encrypted: true, timestamp: '2026-05-26T08:10:00Z', requires_leia: false },
  { id: 'msg-4', channel: 'hologram_email', sender: 'Bail Organa', content: 'Meeting request for next week', status: 'completed', category: 'calendar_booking', owner: 'General Leia', risk_score: 0, encrypted: false, timestamp: '2026-05-26T08:15:00Z', requires_leia: true },
]

const mockTasks = [
  { id: 'task-1', owner: 'Han Solo', assigned_team: 'Logistics Team', title: 'Arrange fuel delivery', priority: 'high', status: 'pending' },
  { id: 'task-2', owner: 'General Leia', assigned_team: 'Executive Office', title: 'Schedule meeting with Bail Organa', priority: 'medium', status: 'pending' },
]

const mockCalendar = [
  { message_id: 'msg-4', requestor: 'Bail Organa', subject: 'Weekly strategy meeting' },
]

const mockBriefingText = 'Good morning, General Leia.\n\nToday we processed 4 requests.\n- 1 threats blocked\n- 1 encrypted\n- 2 completed\n\nKey items await your decision.'

const mockInbox = {
  total_messages: 4,
  completed: 2,
  quarantined: 1,
  encrypted: 1,
  needs_attention: [
    { id: 'msg-4', sender: 'Bail Organa', channel: 'hologram_email', category: 'calendar_booking', subject: 'Meeting request for next week', priority: 'medium', encrypted: false, status: 'completed' },
  ],
  delegation: { 'Han Solo': 1, 'General Leia': 1, 'Security Team': 1, 'Yoda': 1 },
  schedule: [
    { time: '10:00', subject: 'Weekly strategy meeting', requestor: 'Bail Organa' },
  ],
  open_tasks: ['task-1', 'task-2'],
}

const mockIntegrations = {
  gmail: true, calendar: true, clickup: false, whatsapp: true, discord: false,
}

export const handlers = [
  http.get(`${BASE}/`, () => HttpResponse.json({ status: 'ok', service: 'Rebel Operations Engine' })),

  http.get(`${BASE}/messages`, () => HttpResponse.json({ data: mockMessages })),

  http.get(`${BASE}/messages/:id`, ({ params }) => {
    const msg = mockMessages.find(m => m.id === params.id)
    return msg ? HttpResponse.json(msg) : HttpResponse.json({ error: 'Not found' }, { status: 404 })
  }),

  http.get(`${BASE}/agents`, () => HttpResponse.json({
    agents: ['IntakeAgent', 'DarkSideSecurityAgent', 'C3POClassifierAgent', 'RoutingAgent', 'YodaEncryptionAgent', 'CalendarAgent', 'NotificationAgent', 'ReportingAgent', 'ErrorProtocolAgent'],
  })),

  http.get(`${BASE}/briefing`, () => HttpResponse.json({ briefing: mockBriefingText })),

  http.get(`${BASE}/calendar`, () => HttpResponse.json({ data: mockCalendar })),

  http.get(`${BASE}/tasks`, () => HttpResponse.json({ data: mockTasks })),

  http.get(`${BASE}/requests/:id/trace`, ({ params }) => HttpResponse.json({
    request_id: params.id,
    pipeline: ['IntakeAgent', 'DarkSideSecurityAgent', 'C3POClassifierAgent', 'RoutingAgent'],
    status: 'completed',
  })),

  http.post(`${BASE}/intake`, async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({
      status: 'completed',
      category: 'logistics',
      owner: 'Han Solo',
      risk_score: 10,
      encrypted: false,
      message_id: `msg-${Date.now()}`,
    })
  }),

  http.post(`${BASE}/reset`, () => HttpResponse.json({ status: 'reset' })),

  http.post(`${BASE}/demo/load`, () => HttpResponse.json({
    loaded: 4,
    results: [
      { status: 'completed', encrypted: false },
      { status: 'quarantined', encrypted: false },
      { status: 'completed', encrypted: true },
      { status: 'completed', encrypted: false },
    ],
  })),

  http.get(`${BASE}/briefing/inbox`, () => HttpResponse.json(mockInbox)),

  http.get(`${BASE}/integrations`, () => HttpResponse.json(mockIntegrations)),

  http.post(`${BASE}/briefings/generate`, () => HttpResponse.json({ status: 'generated' })),
]
