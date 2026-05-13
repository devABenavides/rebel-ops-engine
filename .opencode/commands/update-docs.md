---
description: Review or update project documentation
agent: build
---

Use the documentation-maintainer skill.

If I asked for a documentation review, stay in read-only mode and do not edit files.

If I explicitly asked to update documentation, only modify documentation-related files.

Do not modify application source code.
Do not modify package files.
Do not install dependencies.
Do not run formatters.
Do not include fake or unsupported project details.
Never include real secrets.

Summarize all documentation files reviewed or changed.
