---
name: mental-load-journal
id: OC-0149
version: 1.0.0
description: "Mental Load Journal - Prompt daily reflection and surface patterns over time"
env:
  - OPENAI_API_KEY
commands:
  - reflect
  - journal
  - patterns
  - mood-trend
---

# Mental Load Journal

Daily guided reflection with AI-powered pattern recognition. Track your mental load, surface recurring stressors, and gain insight into your wellbeing over time.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `OPENAI_API_KEY` — for AI reflection prompts and pattern analysis

## Commands

| Command | Description |
|---------|-------------|
| `reflect` | Start a guided daily reflection session |
| `journal` | Write a free-form journal entry |
| `patterns` | Surface recurring themes and patterns |
| `mood-trend` | View mood trend over time |

## Usage

```bash
export OPENAI_API_KEY="your_key"

# Start a guided reflection
python3 scripts/mental_load_journal.py reflect

# Write a journal entry
python3 scripts/mental_load_journal.py journal --text "Feeling overwhelmed with deadlines..."

# Surface patterns from the last 30 days
python3 scripts/mental_load_journal.py patterns --days 30

# View mood trend
python3 scripts/mental_load_journal.py mood-trend --days 14
```
