---
description: Run a read-only repository audit
agent: plan
---

Use the repo-audit skill to audit this repository.

Strictly follow read-only mode.

During the security review portion, invoke the `security-auditor` subagent only if the repository contains security-sensitive areas such as authentication, authorization, API routes, server actions, environment variables, secrets handling, database access, payments, webhooks, file uploads, user data, admin functionality, third-party integrations, or public-facing backend endpoints.

Do not edit files.
Do not create files.
Do not install dependencies.
Do not run formatters or fix commands.
Stop after the audit report.
