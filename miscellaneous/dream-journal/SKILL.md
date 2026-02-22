---
name: dream-journal
id: OC-0172
version: 1.0.0
description: "Dream Journal - Log and interpret dreams using symbolic analysis"
env:
  - OPENAI_API_KEY
commands:
  - log
  - interpret
  - list
  - themes
---

# Dream Journal

Log dreams, get AI-powered symbolic interpretations, and track recurring themes over time.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `OPENAI_API_KEY` — for AI dream interpretation

## Commands

| Command | Description |
|---------|-------------|
| `log` | Log a new dream |
| `interpret` | Get symbolic interpretation of a dream |
| `list` | Browse past dream entries |
| `themes` | Analyze recurring themes |

## Usage

```bash
export OPENAI_API_KEY="your_key"

# Log a dream
python3 scripts/dream_journal.py log --dream "I was flying over a city at night..."

# Interpret a dream
python3 scripts/dream_journal.py interpret --dream-id DREAM_ID

# List all dreams
python3 scripts/dream_journal.py list

# Find recurring themes
python3 scripts/dream_journal.py themes --days 30
```
