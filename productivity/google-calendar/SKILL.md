---
name: google-calendar
id: OC-0133
version: 1.0.0
description: "Google Calendar - Manage Google Calendar events and check availability"
env:
  - GOOGLE_CALENDAR_TOKEN
  - GOOGLE_CALENDAR_ID
commands:
  - list-events
  - create-event
  - update-event
  - delete-event
  - check-availability
---

# Google Calendar

Manage Google Calendar events and check availability from the CLI using the Google Calendar API.

## Prerequisites

- `GOOGLE_CALENDAR_TOKEN` — OAuth 2.0 bearer access token with `calendar` scope
- `GOOGLE_CALENDAR_ID` — Calendar ID (default: `primary`)
- `pip install requests`

## Commands

| Command | Description |
|---------|-------------|
| `list-events` | List upcoming calendar events |
| `create-event` | Create a new calendar event |
| `update-event` | Update an existing event |
| `delete-event` | Delete an event |
| `check-availability` | Check if a time slot is free |

## Usage

```bash
# List upcoming events
python google_calendar.py list-events

# List events in a date range
python google_calendar.py list-events --time-min "2024-12-01T00:00:00Z" --time-max "2024-12-31T23:59:59Z" --max-results 20

# Create an event
python google_calendar.py create-event --title "Team Standup" --start "2024-12-15T09:00:00" --end "2024-12-15T09:30:00" --description "Daily sync"

# Create event with attendees
python google_calendar.py create-event --title "Meeting" --start "2024-12-15T14:00:00" --end "2024-12-15T15:00:00" --attendees "alice@example.com,bob@example.com"

# Update an event
python google_calendar.py update-event --event-id EVENT_ID --title "Updated Title"

# Delete an event
python google_calendar.py delete-event --event-id EVENT_ID

# Check availability
python google_calendar.py check-availability --start "2024-12-15T14:00:00Z" --end "2024-12-15T15:00:00Z"
```
