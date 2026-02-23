---
name: chaos-monkey
id: OC-0183
version: 1.0.0
description: "Chaos Monkey for Skills - Randomly inject network failures or bad inputs to test skill resilience"
env: []
commands:
  - run
  - list-scenarios
  - report
---

# Chaos Monkey for Skills

Randomly inject faults — network failures, bad inputs, missing env vars, and malformed arguments — to test skill resilience under adverse conditions.

## Prerequisites

- Python 3.8+

## Commands

| Command | Description |
|---------|-------------|
| `run` | Run chaos tests against a target skill |
| `list-scenarios` | List all available fault injection scenarios |
| `report` | Show a summary report of the last chaos run |

## Usage

```bash
# Run chaos tests against a skill (random scenario selection)
python3 scripts/chaos_monkey.py run --skill timezone-converter

# Run a specific chaos scenario
python3 scripts/chaos_monkey.py run --skill gmail-triage --scenario missing-env

# Run all scenarios against a skill
python3 scripts/chaos_monkey.py run --skill google-calendar --all-scenarios

# List available fault scenarios
python3 scripts/chaos_monkey.py list-scenarios

# Show report from the last run (saved to chaos_report.json)
python3 scripts/chaos_monkey.py report --file chaos_report.json
```
