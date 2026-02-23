---
name: skill-runner-cli
id: OC-0178
version: 1.0.0
description: "Skill Runner CLI - A unified CLI to execute any skill with defined inputs"
env: []
commands:
  - run
  - list
  - info
  - validate
---

# Skill Runner CLI

A unified meta-runner that discovers, lists, and executes any OpenClaw skill from a single entry point.

## Prerequisites

- Python 3.8+

## Commands

| Command | Description |
|---------|-------------|
| `run` | Execute a skill by name with arguments |
| `list` | List all available skills |
| `info` | Show details for a skill |
| `validate` | Validate a skill's structure |

## Usage

```bash
# List all available skills
python3 scripts/skill_runner_cli.py list

# List skills in a category
python3 scripts/skill_runner_cli.py list --category productivity

# Show skill info
python3 scripts/skill_runner_cli.py info --skill google-calendar

# Run a skill
python3 scripts/skill_runner_cli.py run --skill timezone-converter -- convert --time "2024-12-15 09:00" --from-zone "America/New_York" --to-zones "Europe/London"

# Validate a skill
python3 scripts/skill_runner_cli.py validate --skill gmail-triage
```
