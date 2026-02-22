---
name: meeting-scribe
id: OC-0110
version: 1.0.0
description: "Meeting Scribe - Live transcription and action item extraction from meetings"
env:
  - OPENAI_API_KEY
commands:
  - transcribe
  - extract-action-items
  - generate-summary
  - export-notes
---

# Meeting Scribe

Transcribe meeting recordings and automatically extract action items, decisions, and summaries.

## Prerequisites

- `OPENAI_API_KEY` — OpenAI API key

## Commands

| Command | Description |
|---------|-------------|
| `transcribe` | Transcribe audio to text |
| `extract-action-items` | Extract action items from a transcript |
| `generate-summary` | Generate a meeting summary |
| `export-notes` | Export formatted meeting notes |

## Usage

```bash
export OPENAI_API_KEY="sk-..."

python3 scripts/meeting_scribe.py transcribe --file standup.mp3 --output standup.txt
python3 scripts/meeting_scribe.py extract-action-items --transcript-file standup.txt
python3 scripts/meeting_scribe.py generate-summary --transcript-file standup.txt --format detailed
python3 scripts/meeting_scribe.py export-notes --transcript-file standup.txt --output-format md
```
