---
description: Evaluate the full OpenCode session across all skills, commands, agents, changes, validation, and final outcomes
agent: plan
---

Use the workflow-evaluator skill in Session-Wide Evaluation Mode.

Evaluate everything we used in this session.

Review the full workflow, including:

- /repo-audit
- @security-auditor, if used
- /test-strategy, if used
- /implement-audit-plan, if used
- /update-docs, if used
- approvals or scope boundaries given by the user
- validation commands
- git status
- git diff
- changed files
- final summaries
- relevant `.opencode` skill, command, and agent files

Tell me:

- Whether the overall workflow was good
- What worked well
- What failed
- Whether the workflows were used in the right order
- Whether each skill followed its rules
- Whether approval boundaries were respected
- Whether implementation stayed within approved scope
- Whether `@security-auditor` was invoked when it should have been
- Whether security review was appropriate
- Whether testing review was useful
- Whether documentation changes were useful
- Whether validation was sufficient
- What skill prompts, command prompts, or agent prompts should be improved

Strictly follow read-only mode.

Do not edit files.
Do not create files.
Do not modify `.opencode`.
Do not modify application source code.
Do not install dependencies.
Do not run formatters.
Do not run tests unless explicitly asked.

If the session history is available in context, evaluate it directly.

If the session history is not available, inspect what you can from the repository, git status, git diff, and saved reports.

If there is not enough evidence to evaluate the full session, say what is missing and ask for the combined session output.

Return:

- Overall verdict
- Session timeline
- Scorecard
- What worked
- What failed
- Scope or safety issues
- False positives or weak claims
- Missed opportunities
- Exact recommendations to improve the relevant skill, command, or agent prompts
- Suggested patch text, if useful
- Final recommendation

Do not apply improvements unless I explicitly approve them.
