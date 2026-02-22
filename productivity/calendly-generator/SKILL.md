---
name: calendly-generator
id: OC-0134
version: 1.0.0
description: "Calendly Link Generator - Create one-off scheduling links with custom constraints"
env:
  - CALENDLY_TOKEN
commands:
  - list-event-types
  - create-link
  - list-links
  - deactivate-link
  - get-scheduled-events
---

# Calendly Link Generator

Generate one-off Calendly scheduling links with custom constraints directly from the terminal.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `CALENDLY_TOKEN` — Personal access token from Calendly developer settings

## Commands

| Command | Description |
|---------|-------------|
| `list-event-types` | List all available event types |
| `create-link` | Create a single-use scheduling link |
| `list-links` | List existing single-use links |
| `deactivate-link` | Deactivate a single-use link |
| `get-scheduled-events` | List scheduled events |

## Usage

```bash
export CALENDLY_TOKEN="your_token_here"

# List all event types
python3 scripts/calendly_generator.py list-event-types

# Create a one-time scheduling link for a specific event type
python3 scripts/calendly_generator.py create-link --event-type-uri "https://api.calendly.com/event_types/UUID"

# Create a link with max uses
python3 scripts/calendly_generator.py create-link --event-type-uri "https://api.calendly.com/event_types/UUID" --max-event-count 1

# List all single-use links
python3 scripts/calendly_generator.py list-links

# Deactivate a link
python3 scripts/calendly_generator.py deactivate-link --link-uri "https://api.calendly.com/one_off_event_type_invites/UUID"

# Get scheduled events (next 7 days)
python3 scripts/calendly_generator.py get-scheduled-events --days 7
```
