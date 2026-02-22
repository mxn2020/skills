---
name: sleep-analyst
id: OC-0143
version: 1.0.0
description: "Sleep Analyst - Correlate sleep data with productivity metrics"
env:
  - OURA_TOKEN
commands:
  - log-sleep
  - analyze
  - weekly-report
  - correlate
---

# Sleep Analyst

Track and analyze sleep quality, correlate with productivity, and get AI-powered insights using Oura Ring data or manual logging.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `OURA_TOKEN` — Oura Ring personal access token (optional, for auto-sync)

## Commands

| Command | Description |
|---------|-------------|
| `log-sleep` | Manually log sleep data |
| `analyze` | Analyze sleep patterns over time |
| `weekly-report` | Generate a weekly sleep report |
| `correlate` | Correlate sleep with productivity scores |

## Usage

```bash
export OURA_TOKEN="your_oura_token"  # optional

# Log sleep manually
python3 scripts/sleep_analyst.py log-sleep --bedtime "23:30" --wake "07:00" --quality 8 --notes "Restful"

# Pull and analyze from Oura (last 7 days)
python3 scripts/sleep_analyst.py analyze --days 7

# Generate weekly report
python3 scripts/sleep_analyst.py weekly-report

# Correlate sleep score with productivity
python3 scripts/sleep_analyst.py correlate --productivity-scores "8,7,6,9,8,7,5"
```
