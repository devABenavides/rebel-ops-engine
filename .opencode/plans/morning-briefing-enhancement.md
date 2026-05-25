# Morning Briefing Enhancement Plan

## 1. Backend — Augment `/api/briefing/inbox` (`main.py`)

**File:** `rebel_ops_engine/main.py` — `briefing_inbox()` function (lines 460-506)

### Changes:

#### a) Enhance `needs_attention` items — add per-message fields:

Add `channel`, `status`, `encrypted`, `risk_score` to each dict in the `needs_attention` list comprehension:

```python
needs_attention = [
    {
        "id": m.id, "sender": m.sender,
        "category": m.category.value if m.category else "unknown",
        "priority": m.priority,
        "subject": m.subject or m.content[:80],
        "timestamp": m.timestamp.isoformat(),
        "channel": m.channel.value,
        "status": m.status.value,
        "encrypted": m.encrypted,
        "risk_score": m.risk_score,
    }
    for m in msgs if m.requires_leia
]
```

#### b) Add `delegation` breakdown:

Insert before the `return jsonify({` line:

```python
delegation = {}
for m in msgs:
    owner = m.owner.value if m.owner else "Unassigned"
    delegation[owner] = delegation.get(owner, 0) + 1
```

#### c) Add `messages` array:

Insert before the `return jsonify({` line:

```python
messages_list = [
    {
        "id": m.id, "channel": m.channel.value,
        "sender": m.sender, "category": m.category.value if m.category else "unknown",
        "status": m.status.value, "priority": m.priority,
        "encrypted": m.encrypted, "owner": m.owner.value if m.owner else None,
        "assigned_team": m.assigned_team,
        "subject": m.subject or m.content[:80],
        "content": m.content[:200],
        "risk_score": m.risk_score,
        "timestamp": m.timestamp.isoformat(),
    }
    for m in sorted(msgs, key=lambda x: x.timestamp, reverse=True)
]
```

#### d) Include in response:

Add `"delegation": delegation,` and `"messages": messages_list,` before `"schedule"`.

---

## 2. Frontend — Restructure `MorningBriefing.jsx`

**File:** `rebel_ops_engine/frontend/src/components/MorningBriefing.jsx`

### CSS additions to `STYLE`:

```css
/* Channel badges */
.ch-badge {
  font-family: var(--mono); font-size: 10px; padding: 2px 8px;
  border-radius: 4px; letter-spacing: 0.04em; font-weight: 600;
  display: inline-flex; align-items: center; gap: 4px;
}
.ch-badge.whatsapp { background: #e3f0e3; color: #2d6b3f; }
.ch-badge.email { background: #e3ebf2; color: #3a6a8a; }

/* Status badges (same colors as App.css) */
.st-badge {
  font-family: var(--mono); font-size: 10px; padding: 2px 8px;
  border-radius: 4px; letter-spacing: 0.04em; font-weight: 600;
}
.st-badge.completed { background: #1b3d2e; color: #4caf7d; }
.st-badge.encrypted { background: #2d2b1b; color: #ffd54f; }
.st-badge.quarantined { background: #3d1b1b; color: #ef5350; }
.st-badge.error { background: #3d1b1b; color: #ef5350; }
.st-badge.pending { background: #1e2435; color: #90a4ae; }

/* Enhanced attention item with left accent */
.attention-item {
  border-left: 4px solid var(--line-strong);
}
.attention-item.priority-critical { border-left-color: #c8775c; }
.attention-item.priority-high { border-left-color: #8e6f1f; }
.attention-item.priority-medium { border-left-color: #4a6e8a; }
.attention-item.priority-low { border-left-color: #8e8e88; }
.attention-header {
  display: flex; align-items: center; gap: 8px; margin-bottom: 4px;
}
.attention-channel {
  font-family: var(--mono); font-size: 11px; color: var(--muted);
  display: inline-flex; align-items: center; gap: 4px;
}

/* Message list items */
.msg-item {
  background: var(--paper-elev); border: 1px solid var(--line);
  border-radius: var(--r); padding: 14px 18px;
  display: grid; grid-template-columns: auto 1fr auto; gap: 12px;
  align-items: center; cursor: pointer; transition: all 0.15s;
}
.msg-item:hover { border-color: var(--line-strong); }
.msg-item .m-channel { font-size: 16px; }
.msg-item .m-sender { font-size: 13px; font-weight: 600; color: var(--ink); }
.msg-item .m-subject { font-size: 12px; color: var(--ink-soft); margin-top: 2px; }
.msg-item .m-badges { display: flex; gap: 6px; align-items: center; }

/* Sidebar calendar card */
.side-calendar { margin-bottom: 14px; }
.side-calendar .sched-row {
  grid-template-columns: 60px 8px 1fr; gap: 10px; padding: 10px 14px;
  border-left: none; border-right: none;
}
.side-calendar .sched-row .dot { width: 8px; height: 8px; }
.side-calendar .sched-row .time { font-size: 11px; }
.side-calendar .sched-row .title { font-size: 13px; }

/* Delegation list */
.del-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 6px 0; font-size: 13px; color: var(--ink-soft);
  border-bottom: 1px dashed var(--hairline);
}
.del-row:last-child { border-bottom: none; }
.del-row .del-count {
  font-family: var(--mono); font-size: 13px; font-weight: 700; color: var(--rebel);
}
```

### Layout restructure:

New section order in the JSX render:

```
b-main grid (1fr / 280px)
├── main column
│   ├── Greeting (meta-row stats)
│   ├── i. Requests needing your decision (enhanced attention list)
│   ├── ii. Operations summary (stat cards, moved up)
│   ├── iii. Today, quietly (wins, moved up)
│   ├── iv. Open tasks in progress (moved down)
│   └── v. All messages (new section)
│
└── sidebar
    ├── Today's Calendar (moved from main, as side-card)
    ├── first-thing (your first action)
    ├── Delegation breakdown (new side-card)
    ├── Quick actions
    └── Connected sources
```

### Attention item render (enhanced):

Replace the current attention-item render with:

```jsx
{data.needs_attention.map((item) => {
  const channelIcon = item.channel === 'intergalactic_whatsapp' ? '\uD83D\uDCAC' : '\u2709\uFE0F';
  const channelLabel = item.channel === 'intergalactic_whatsapp' ? 'WhatsApp' : 'Hologram Email';
  const priorityClass = item.priority === 'critical' ? 'urgent' : item.priority === 'high' ? 'high' : 'normal';
  return (
    <div key={item.id}
      className={`attention-item priority-${item.priority}`}
      onClick={() => toast({ title: item.sender, body: `<strong>${item.category.replace(/_/g, ' ')}</strong><br/>${item.subject}<br/>Priority: ${item.priority} · ${channelLabel}` })}>
      <span className="attention-av" style={{background: getInitialBg(item.sender)}}>{getInitials(item.sender)}</span>
      <div>
        <div className="attention-header">
          <span className="attention-channel">{channelIcon} {channelLabel}</span>
          <span className="attention-meta">{item.sender} · {item.category.replace(/_/g, ' ')}</span>
        </div>
        <div className="attention-subject">{item.subject.slice(0, 100)}</div>
      </div>
      <div style={{display: 'flex', flexDirection: 'column', gap: 4, alignItems: 'flex-end'}}>
        <span className={`attention-tag ${priorityClass}`}>{item.priority}</span>
        {item.encrypted && <span className="st-badge encrypted">ENCRYPTED</span>}
        {item.status === 'quarantined' && <span className="st-badge quarantined">BLOCKED</span>}
      </div>
    </div>
  );
})}
```

### All messages section (new):

```jsx
{data.messages?.length > 0 && (
  <section className="b-block">
    <div className="head">
      <h2><span className="ord">v.</span>All requests</h2>
      <span className="meta">{data.messages.length} total</span>
    </div>
    <div style={{display: 'flex', flexDirection: 'column', gap: 8}}>
      {data.messages.map((m) => {
        const channelIcon = m.channel === 'intergalactic_whatsapp' ? '\uD83D\uDCAC' : '\u2709\uFE0F';
        const statusBadge = m.status === 'completed' ? 'completed'
          : m.status === 'quarantined' ? 'quarantined'
          : m.status === 'error' ? 'error'
          : 'pending';
        return (
          <div key={m.id} className="msg-item" onClick={() => toast({ title: m.sender, body: `<strong>${m.category.replace(/_/g, ' ')}</strong><br/>${m.subject}<br/>Status: ${m.status}` })}>
            <span className="m-channel">{channelIcon}</span>
            <div>
              <div className="m-sender">{m.sender}</div>
              <div className="m-subject">{m.subject.slice(0, 80)}</div>
            </div>
            <div className="m-badges">
              {m.encrypted && <span className="st-badge encrypted">ENCRYPTED</span>}
              <span className={`st-badge ${statusBadge}`}>{m.status.toUpperCase()}</span>
            </div>
          </div>
        );
      })}
    </div>
  </section>
)}
```

### Calendar moved to sidebar:

Replace the existing calendar section in main with a sidebar card:

```jsx
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
```

Remove the old calendar section from the main column (currently `section.b-block` with `ord` = `iii`).

### Delegation breakdown sidebar card (new):

```jsx
{data.delegation && Object.keys(data.delegation).length > 0 && (
  <div className="side-card">
    <h4>{'\uD83D\uDCCB'} Today's delegation</h4>
    {Object.entries(data.delegation)
      .sort((a, b) => b[1] - a[1])
      .map(([owner, count]) => (
        <div key={owner} className="del-row">
          <span>{owner}</span>
          <span className="del-count">{count}</span>
        </div>
      ))}
  </div>
)}
```

### Updated section numbering:

- i. Requests needing your decision
- ii. Operations summary
- iii. Today, quietly (wins)
- iv. Open tasks in progress
- v. All requests (new)

---

## 3. Run validation

```bash
cd rebel_ops_engine && python -m ruff check .
```
