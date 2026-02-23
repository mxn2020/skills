---
name: symptom-checker
id: OC-0146
version: 1.0.0
description: "Symptom Checker - Basic triage based on described symptoms (with medical disclaimers)"
env:
  - OPENAI_API_KEY
commands:
  - check
  - urgent
  - log-symptom
  - history
---

# Symptom Checker

Basic symptom triage powered by AI. Describes possible causes and urgency level. **Not a substitute for professional medical advice.**

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `OPENAI_API_KEY` — for AI-based symptom analysis

## Commands

| Command | Description |
|---------|-------------|
| `check` | Analyze described symptoms |
| `urgent` | Quick check if symptoms require emergency care |
| `log-symptom` | Log a symptom for tracking |
| `history` | Show symptom history |

## Usage

```bash
export OPENAI_API_KEY="your_key"

# Check symptoms
python3 scripts/symptom_checker.py check --symptoms "headache, fatigue, mild fever for 2 days"

# Quick urgency assessment
python3 scripts/symptom_checker.py urgent --symptoms "chest pain and shortness of breath"

# Log a symptom
python3 scripts/symptom_checker.py log-symptom --symptom "headache" --severity 4 --notes "started after work"

# View symptom history
python3 scripts/symptom_checker.py history --days 7
```
