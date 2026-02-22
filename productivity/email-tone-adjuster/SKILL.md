---
name: email-tone-adjuster
id: OC-0139
version: 1.0.0
description: "Email Tone Adjuster - Rewrite drafts to match a target tone (formal, concise, friendly)"
env:
  - OPENAI_API_KEY
commands:
  - adjust
  - analyze
  - suggest-subject
---

# Email Tone Adjuster

Rewrite email drafts to match a target tone using AI. Supports formal, concise, friendly, assertive, and empathetic styles.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `OPENAI_API_KEY` — OpenAI API key

## Commands

| Command | Description |
|---------|-------------|
| `adjust` | Rewrite an email draft in a new tone |
| `analyze` | Analyze the current tone of an email |
| `suggest-subject` | Generate subject line suggestions |

## Usage

```bash
export OPENAI_API_KEY="your_key"

# Adjust tone from a file
python3 scripts/email_tone_adjuster.py adjust --file draft.txt --tone formal

# Adjust tone from inline text
python3 scripts/email_tone_adjuster.py adjust --text "Hey can u send me the report asap" --tone professional

# Analyze the tone of an email
python3 scripts/email_tone_adjuster.py analyze --file draft.txt

# Generate subject line suggestions
python3 scripts/email_tone_adjuster.py suggest-subject --file draft.txt --count 5
```
