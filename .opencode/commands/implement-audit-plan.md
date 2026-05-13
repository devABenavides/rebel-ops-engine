---
description: Implement approved audit findings
agent: build
---

Use the implement-audit-plan skill.

Implement only the audit findings I explicitly approved.

Keep the diff focused and safe.
Check git status first.
Preserve user changes.

If the approved implementation touches security-sensitive areas, invoke the `security-auditor` subagent before finalizing.

Run relevant validation commands.
Summarize all changes, commands, results, security review outcome, and remaining risks.
