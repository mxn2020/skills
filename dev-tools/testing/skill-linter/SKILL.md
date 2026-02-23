---
name: skill-linter
id: OC-0182
version: 1.0.0
description: "Skill Linter - Validate SKILL.md structure and ensure scripts follow OpenClaw conventions"
env: []
commands:
  - lint
  - lint-all
  - fix-report
---

# Skill Linter

Validate that skills follow OpenClaw conventions. Checks SKILL.md frontmatter, script structure, and code quality standards.

## Prerequisites

- Python 3.8+

## Commands

| Command | Description |
|---------|-------------|
| `lint` | Lint a specific skill |
| `lint-all` | Lint all skills in the repository |
| `fix-report` | Generate a report of all issues |

## Usage

```bash
# Lint a specific skill
python3 scripts/skill_linter.py lint --skill gmail-triage

# Lint all skills
python3 scripts/skill_linter.py lint-all

# Lint a specific category
python3 scripts/skill_linter.py lint-all --category health

# Generate fix report
python3 scripts/skill_linter.py fix-report --output issues.md
```
