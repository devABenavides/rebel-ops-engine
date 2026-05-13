import React, { useState } from 'react'
import CommandCenter from './components/CommandCenter.jsx'
import WorkflowGraph from './components/WorkflowGraph.jsx'
import Briefing from './components/Briefing.jsx'
import MessageForm from './components/MessageForm.jsx'
import Calendar from './components/Calendar.jsx'
import Tasks from './components/Tasks.jsx'
import ErrorBoundary from './components/ErrorBoundary.jsx'
import { api } from './api.js'

const PAGES = {
  command: { label: '\uD83D\uDCCA Command Center', cmp: CommandCenter },
  architecture: { label: '\uD83D\uDD17 Architecture', cmp: WorkflowGraph },
  briefing: { label: '\uD83D\uDCC4 Briefing', cmp: Briefing },
  intake: { label: '\uD83D\uDCE9 Send Message', cmp: MessageForm },
  calendar: { label: '\uD83D\uDCC5 Calendar', cmp: Calendar },
  tasks: { label: '\uD83D\uDCDD Tasks', cmp: Tasks },
}

export default function App() {
  const [page, setPage] = useState('command')
  const [refreshKey, setRefreshKey] = useState(0)
  const [loading, setLoading] = useState(false)
  const [demoMsg, setDemoMsg] = useState('')

  const refresh = () => setRefreshKey((k) => k + 1)

  const handleDemo = async () => {
    setLoading(true)
    setDemoMsg('')
    try {
      const res = await api.demoLoad()
      setDemoMsg(
        `Loaded ${res.loaded} demo messages. ` +
        `${res.results.filter((r) => r.status === 'quarantined').length} threats blocked, ` +
        `${res.results.filter((r) => r.encrypted).length} encrypted.`
      )
      refresh()
    } catch {
      setDemoMsg('Failed to load demo messages.')
    }
    setLoading(false)
  }

  const handleReset = async () => {
    setLoading(true)
    try {
      await api.reset()
      setDemoMsg('State reset.')
      refresh()
    } catch {
      setDemoMsg('Reset failed.')
    }
    setLoading(false)
  }

  const PageComponent = PAGES[page].cmp

  return (
    <div className="app">
      <div className="sidebar">
        <h1>
          REBEL OPS
          <small>Operations Engine v2.0</small>
        </h1>
        <nav>
          {Object.entries(PAGES).map(([key, { label }]) => (
            <button key={key} className={page === key ? 'active' : ''} onClick={() => setPage(key)}>
              {label}
            </button>
          ))}
        </nav>
        <div style={{ padding: '20px 16px 0', borderTop: '1px solid #2a3346', marginTop: 20 }}>
          <button className="btn btn-success" style={{ width: '100%', marginBottom: 8 }} onClick={handleDemo} disabled={loading}>
            Load Demo
          </button>
          <button className="btn btn-outline" style={{ width: '100%' }} onClick={handleReset} disabled={loading}>
            Reset State
          </button>
          {demoMsg && <div style={{ fontSize: 11, color: '#8892a4', marginTop: 8 }}>{demoMsg}</div>}
        </div>
      </div>
      <div className="main">
        <ErrorBoundary key={page}>
          <PageComponent key={page + '-' + refreshKey} onMessageSent={refresh} />
        </ErrorBoundary>
      </div>
    </div>
  )
}
