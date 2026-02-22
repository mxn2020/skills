---
name: language-tutor
id: OC-0175
version: 1.0.0
description: "Language Tutor - Run interactive vocabulary drills and grammar corrections"
env:
  - OPENAI_API_KEY
commands:
  - vocab-drill
  - grammar-check
  - translate
  - lesson
  - progress
---

# Language Tutor

Interactive language learning with vocabulary drills, grammar corrections, translations, and personalized lessons.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `OPENAI_API_KEY` — for AI-powered tutoring

## Commands

| Command | Description |
|---------|-------------|
| `vocab-drill` | Run a vocabulary quiz session |
| `grammar-check` | Check and correct grammar in a sentence |
| `translate` | Translate text with explanations |
| `lesson` | Get a mini-lesson on a grammar topic |
| `progress` | View learning progress |

## Usage

```bash
export OPENAI_API_KEY="your_key"

# Vocabulary drill (Spanish, beginner)
python3 scripts/language_tutor.py vocab-drill --language spanish --level beginner --count 10

# Grammar check
python3 scripts/language_tutor.py grammar-check --text "I goes to store yesterday" --language english

# Translate with explanation
python3 scripts/language_tutor.py translate --text "Bon vivant" --from-lang french --to-lang english --explain

# Get a mini grammar lesson
python3 scripts/language_tutor.py lesson --language french --topic "subjunctive mood"
```
