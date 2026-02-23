---
name: meditation-guide
id: OC-0144
version: 1.0.0
description: "Meditation Guide - Generate and narrate personalized guided meditation scripts"
env:
  - OPENAI_API_KEY
commands:
  - generate
  - list-sessions
  - log-session
  - streak
---

# Meditation Guide

Generate personalized guided meditation scripts, track sessions, and maintain your practice streak.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `OPENAI_API_KEY` — for AI-generated meditation scripts

## Commands

| Command | Description |
|---------|-------------|
| `generate` | Generate a guided meditation script |
| `list-sessions` | List past meditation sessions |
| `log-session` | Log a completed meditation session |
| `streak` | Show current meditation streak |

## Usage

```bash
export OPENAI_API_KEY="your_key"

# Generate a 10-minute stress relief meditation
python3 scripts/meditation_guide.py generate --duration 10 --focus "stress relief"

# Generate a sleep meditation
python3 scripts/meditation_guide.py generate --duration 15 --focus "sleep" --style "body scan"

# Log a completed session
python3 scripts/meditation_guide.py log-session --duration 10 --notes "Felt calm"

# Show streak
python3 scripts/meditation_guide.py streak
```
