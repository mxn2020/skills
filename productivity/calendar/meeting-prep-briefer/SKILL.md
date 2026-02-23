---
name: meeting-prep-briefer
id: OC-0135
version: 1.0.0
description: "Meeting Prep Briefer - Summarize attendees, agenda, and relevant docs before a meeting"
env:
  - GOOGLE_CALENDAR_TOKEN
  - OPENAI_API_KEY
commands:
  - brief
  - list-upcoming
  - summarize-doc
---

# Meeting Prep Briefer

Prepare comprehensive briefings for upcoming meetings by pulling calendar events, attendee info, and generating AI summaries.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `GOOGLE_CALENDAR_TOKEN` — OAuth 2.0 bearer token with calendar scope
- `OPENAI_API_KEY` — OpenAI API key (for AI-generated summaries)

## Commands

| Command | Description |
|---------|-------------|
| `list-upcoming` | List meetings scheduled in the next N hours |
| `brief` | Generate a prep briefing for a specific event |
| `summarize-doc` | Summarize a document URL for meeting context |

## Usage

```bash
export GOOGLE_CALENDAR_TOKEN="your_token"
export OPENAI_API_KEY="your_key"

# List upcoming meetings in the next 24 hours
python3 scripts/meeting_prep_briefer.py list-upcoming --hours 24

# Generate a briefing for the next meeting
python3 scripts/meeting_prep_briefer.py brief --event-id EVENT_ID

# Summarize a document for context
python3 scripts/meeting_prep_briefer.py summarize-doc --url "https://docs.google.com/..."
```
