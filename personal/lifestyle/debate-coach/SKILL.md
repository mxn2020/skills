---
name: debate-coach
id: OC-0176
version: 1.0.0
description: "Debate Coach - Argue both sides of a topic and score the strength of arguments"
env:
  - OPENAI_API_KEY
commands:
  - both-sides
  - steelman
  - score
  - practice
---

# Debate Coach

Explore both sides of any topic, steelman opposing arguments, score argument quality, and practice structured debate.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `OPENAI_API_KEY` — for AI-powered debate analysis

## Commands

| Command | Description |
|---------|-------------|
| `both-sides` | Present arguments for and against a topic |
| `steelman` | Build the strongest version of an argument |
| `score` | Score an argument's logical strength |
| `practice` | Interactive debate practice session |

## Usage

```bash
export OPENAI_API_KEY="your_key"

# Get both sides of a debate topic
python3 scripts/debate_coach.py both-sides --topic "Should AI replace human jobs?"

# Steelman an argument
python3 scripts/debate_coach.py steelman --argument "Taxes should be lower" --side against

# Score an argument
python3 scripts/debate_coach.py score --argument "Nuclear energy is the best solution to climate change because it's carbon-free"

# Practice debate on a topic
python3 scripts/debate_coach.py practice --topic "Universal basic income" --side for
```
