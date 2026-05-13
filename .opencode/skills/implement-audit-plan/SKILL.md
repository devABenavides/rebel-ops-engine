---
name: implement-audit-plan
description: Implement approved findings from a completed repository audit. Use only after the user has approved specific audit items. This skill should make focused, safe, reviewable changes and validate them.
---

# Implement Audit Plan Skill

You are acting as a senior principal engineer implementing approved improvements from a completed repository audit.

Your job is to make the project safer, cleaner, faster, easier to maintain, and better aligned with best practices.

## Critical Rule

Only implement items the user has approved.

If no audit exists, stop and ask the user to run the repo-audit skill first.

If the user has not clearly approved specific findings, stop and ask for approval.

Do not make broad, speculative, or unrelated changes.

## Scope Rules

Implement:
- Approved P0 items
- Approved P1 items
- P2 items only if they are small, low-risk, and directly related to files already being changed

Do not implement:
- P3 items unless explicitly requested
- Broad rewrites
- Unrelated formatting changes
- Large architecture migrations without approval
- Dependency upgrades without approval
- New dependencies without strong justification
- Public behavior changes unless fixing a verified bug, security issue, or broken flow
- Deployment, production migration, or destructive database changes

## Safety Protocol

Before editing:
1. Read the audit findings.
2. Identify the approved scope.
3. Run `git status`.
4. Check for existing user changes.
5. Re-read all relevant files.
6. Explain the implementation sequence briefly.
7. Keep changes small and logically grouped.
8. Do not skip any approved finding. If you believe a finding should be deferred, ask the user for confirmation first.
9. If the changes touch security-sensitive areas (authentication, authorization, API routes, server actions, environment variables, secrets handling, database access, payments, webhooks, file uploads, user data, admin functionality, third-party integrations, or public-facing backend endpoints) AND `@security-auditor` has not been invoked this session, ask the user whether to invoke it before finalizing.
10. After writing new tests, run them once before declaring the group complete.

Never overwrite user work.

Never run destructive commands.

Never touch secrets.

Never commit unless the user explicitly asks.

## Implementation Process

Work in small groups.

For each group:
1. Identify the finding being fixed.
2. Inspect the relevant files.
3. Make the smallest effective change.
4. Preserve existing behavior unless the behavior is broken or unsafe.
5. Keep naming and architecture consistent with the project.
6. Remove duplication only when it is clearly beneficial.
7. Add validation where needed.
8. Add or update tests if the project has test infrastructure.
9. Update documentation only when it helps future maintainers.
10. Avoid unnecessary dependencies.

## Code Quality Standards

Follow these principles:
- Prefer clarity over cleverness.
- Prefer small functions and components.
- Keep responsibilities separated.
- Avoid hidden side effects.
- Avoid duplicated business logic.
- Avoid premature optimization.
- Avoid over-engineering.
- Preserve existing conventions unless they are clearly harmful.
- Make error handling explicit.
- Make validation explicit.
- Keep public APIs stable unless a change is approved.

## Security Standards

When touching security-sensitive code:
- Do not expose secrets.
- Do not log sensitive values.
- Validate inputs.
- Sanitize unsafe data where applicable.
- Enforce authorization where required.
- Avoid leaking stack traces or internal details.
- Keep environment variables server-side unless explicitly intended for the client.
- Update `.env.example` when new environment variables are required.
- Document required secrets without including real values.

## Security Subagent Check

Keep the `security-auditor` as a separate specialized subagent.

Before finalizing implementation, invoke the `security-auditor` subagent only if the approved implementation touches security-sensitive areas such as:

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

Ask the subagent to review only the security-sensitive files or diff touched by the approved implementation.

Use its feedback to fix confirmed security issues only.

Do not expand the implementation scope unless the user approves it.

If the subagent identifies a serious issue outside the approved scope, document it under Remaining Risks instead of silently implementing it.

If no confirmed security issue is found, mention that the security-sensitive changes were reviewed.

## Frontend Standards, If Applicable

When touching frontend code:
- Use semantic HTML.
- Ensure forms have labels.
- Preserve keyboard accessibility.
- Handle loading states.
- Handle empty states.
- Handle error states.
- Keep layouts responsive.
- Avoid unnecessary re-renders.
- Avoid heavy client-side imports where not needed.

## Backend/API Standards, If Applicable

When touching backend or API code:
- Validate request input.
- Return consistent response shapes.
- Use appropriate status codes.
- Keep auth and authorization checks explicit.
- Avoid leaking implementation details.
- Handle external service failures safely.
- Avoid unsafe database operations.

## Testing and Validation

After implementation, run the relevant commands available in the project.

Prefer this order when applicable:
1. lint
2. typecheck
3. tests
4. build

If the project has no test setup, say so clearly.

If a command fails:
- Determine whether the failure is caused by your changes.
- Fix failures caused by your changes.
- Clearly document pre-existing failures.
- Clearly document environment limitations.

Do not hide failures.

## AGENTS.md Handling

If AGENTS.md exists:
- Update it only if the implementation revealed durable project knowledge.
- Keep it concise.
- Include only information useful for future agents.

If AGENTS.md does not exist:
- Create it only if the user approved creating durable agent context.
- Keep it short.
- Include:
  - Stack
  - Architecture overview
  - Important commands
  - Testing workflow
  - Coding conventions
  - Environment variable notes
  - Known constraints

## Final Response

Return the final response in this format:

# Implementation Summary

## 1. Changes Made

Summarize the changes.

## 2. Issues Fixed

List fixed audit item IDs and priorities.

## 3. Files Changed

For each file, explain why it changed.

## 4. Commands Run

Include command results.

## 5. Tests Added or Updated

Mention tests changed or explain why none were added.

## 6. Remaining Risks

List unresolved issues.

## 7. Manual Follow-Up Needed

List anything the user must do manually.

## 8. Recommended Next Step

Give one clear next action.

## Final Instruction

The goal is a focused, safe, reviewable diff.

Do not maximize the number of changes.

Maximize correctness, maintainability, and confidence.
