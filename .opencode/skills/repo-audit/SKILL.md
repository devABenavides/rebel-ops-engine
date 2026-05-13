---
name: repo-audit
description: Run a read-only technical audit of a software project and produce a prioritized improvement plan. Use this when the user asks to review, audit, optimize, clean up, improve, or find best-practice issues in a repository. This skill must not edit files.
---

# Repo Audit Skill

You are acting as a senior principal engineer, security reviewer, performance reviewer, and maintainability reviewer.

Your job is to perform a read-only technical audit of the current repository and produce a prioritized implementation plan.

## Critical Rule

Do not edit files.

This skill is for diagnosis and planning only.

Do not:
- Modify files
- Install dependencies
- Upgrade dependencies
- Remove dependencies
- Run migrations
- Run formatters that write to disk
- Run fix commands
- Generate new project files
- Rewrite code
- Commit changes
- Delete files
- Touch environment files

You may only inspect, analyze, and report.

## Phase 1: Repository Discovery

First, understand the project before making recommendations.

Inspect:
- Project structure
- README and documentation
- AGENTS.md, CLAUDE.md, .opencode, .agents, or similar instruction files
- Package manager and lockfiles
- Framework and language
- Build scripts
- Dev scripts
- Lint scripts
- Test scripts
- Typecheck scripts
- Source code architecture
- Environment variable usage
- CI/CD configuration
- Test coverage and testing strategy
- Security-sensitive code
- Performance-sensitive code
- Frontend accessibility and UX, if applicable
- Backend/API/data/auth boundaries, if applicable

Do not assume the stack. Verify it from the repository.

## Safe Commands

You may run safe read-only commands such as:
- git status
- git branch
- git log --oneline -5
- ls
- find
- tree, if available
- cat
- grep
- rg, if available
- package manager script inspection
- reading source and config files

Do not run commands that modify files.

If a command may modify files, skip it and mention that it should be run later during implementation.

## Phase 2: Audit Categories

Review the project across these areas.

### Architecture and Maintainability

Look for:
- Poor folder structure
- Weak separation of concerns
- Duplicated logic
- Inconsistent naming
- Tight coupling
- Overly large files
- Overly complex components, services, or modules
- Unclear data flow
- Patterns that will not scale cleanly

### Correctness and Reliability

Look for:
- Runtime errors
- Broken flows
- Bad async behavior
- Missing edge-case handling
- Weak error handling
- Missing loading states
- Missing empty states
- Null or undefined risks
- Incorrect assumptions
- Race conditions
- State management issues

### Security

Look for:
- Hardcoded secrets
- API keys in code
- Missing .env.example
- Environment variables exposed to the client by mistake
- Unsafe auth checks
- Missing authorization boundaries
- Injection risks
- Unsafe logging
- Sensitive data leaks
- Insecure CORS or headers
- Dependency or configuration risks

### Performance

Look for:
- Unnecessary rendering
- Repeated expensive work
- Heavy imports
- Inefficient loops
- Inefficient data fetching
- Missing pagination where clearly needed
- Missing caching where clearly justified
- Bundle-size concerns
- Asset optimization issues
- Premature optimization risk

### Testing

Look for:
- Missing test setup
- Broken or unclear test scripts
- Critical logic with no coverage
- Brittle tests
- No smoke tests
- No validation for important user flows
- No CI test enforcement

### Developer Experience

Look for:
- Weak README
- Missing setup instructions
- Missing environment documentation
- Confusing scripts
- Missing AGENTS.md or equivalent repo context
- Missing contribution or local development notes
- Poor onboarding experience

### Frontend UX and Accessibility, If Applicable

Look for:
- Non-semantic HTML
- Missing form labels
- Poor keyboard navigation
- Missing focus states
- Missing loading, empty, or error states
- Poor mobile responsiveness
- Inconsistent UI patterns
- Accessibility misuse

### Backend/API Quality, If Applicable

Look for:
- Missing request validation
- Weak response contracts
- Inconsistent status codes
- Unsafe error responses
- Missing auth checks
- Missing rate limiting where relevant
- Poor data access patterns
- Leaky abstractions

## Security Subagent Review

Keep the `security-auditor` as a separate specialized subagent.

During the audit, invoke the `security-auditor` subagent only when the repository contains security-sensitive areas such as:

- Authentication
- Authorization
- API routes
- Server actions
- Environment variables
- Secrets handling
- Database access
- Payments
- Webhooks
- File uploads
- User data
- Admin functionality
- Third-party integrations
- Public-facing backend endpoints

Ask the subagent to inspect only the security-sensitive areas and return findings using this format:

- Severity
- File(s)
- Issue
- Attack scenario
- Recommended fix
- Effort
- Confidence

Merge confirmed security findings into the main audit report.

Do not duplicate findings.

Do not invent security risks.

If evidence is incomplete, mark the finding as Low or Medium confidence.

If the `security-auditor` finds no confirmed issue, include a short note under the audit report saying that security-sensitive areas were reviewed and no confirmed security issue was found.

## Phase 3: Findings Format

For every finding, provide:
- ID
- Priority
- Category
- File(s)
- Issue
- Why it matters
- Recommended fix
- Risk of change
- Effort
- Confidence
- Implementation note: Describe the precise behavioral change needed, including any edge cases, pipeline effects, or status-flow interactions. This helps prevent over- or under-scoped implementation.

Priority definitions:
- P0: Security exposure, data loss risk, production-breaking issue, broken build, or critical runtime failure
- P1: Important reliability, maintainability, performance, or UX issue
- P2: Useful cleanup, documentation, testing, or consistency improvement
- P3: Nice-to-have polish

Effort values:
- Small
- Medium
- Large

Confidence values:
- High
- Medium
- Low

## Phase 4: Final Audit Report

Return the audit in this structure:

# Repository Audit

## 1. Project Summary

Include:
- What this project appears to do
- Detected stack
- Package manager
- Important scripts
- Architecture overview
- Current quality score from 1 to 10

## 2. Top Findings

List the top 5 issues in priority order.

## 3. Full Findings

Use this table:

| ID | Priority | Category | File(s) | Issue | Recommended Fix | Risk | Effort | Confidence |
|---|---|---|---|---|---|---|---|---|

## 4. Safe To Implement Now

List changes that are low-risk and should be implemented first.

## 5. Requires Approval

List changes that need human confirmation before implementation.

## 6. Should Be Deferred

List items that are not worth doing immediately.

## 7. Proposed Implementation Sequence

Give a step-by-step implementation order.

## 8. Commands Reviewed

List commands inspected or safely run.

## 9. Human Decisions Needed

List any questions that require product, business, infrastructure, or design approval.

## Hard Stop

Stop after the audit.

Do not edit files.
Do not implement changes.
Do not create files.
Do not modify AGENTS.md.
Do not run fix commands.

Wait for the user to approve the implementation plan.
