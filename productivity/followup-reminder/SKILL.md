---
name: followup-reminder
id: OC-0140
version: 1.0.0
description: "Follow-up Reminder - Track sent emails and flag those awaiting a response"
env:
  - GMAIL_TOKEN
commands:
  - scan
  - list-pending
  - mark-resolved
  - add-manual
---

# Follow-up Reminder

Track sent emails and flag those awaiting a response. Scans your Sent folder for emails without replies after a configurable number of days.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `GMAIL_TOKEN` — OAuth 2.0 bearer token with `gmail.readonly` scope

## Commands

| Command | Description |
|---------|-------------|
| `scan` | Scan sent emails for those without replies |
| `list-pending` | Show all tracked pending follow-ups |
| `mark-resolved` | Mark a follow-up as resolved |
| `add-manual` | Manually add a follow-up reminder |

## Usage

```bash
export GMAIL_TOKEN="your_token"

# Scan sent emails for unanswered threads (after 3+ days)
python3 scripts/followup_reminder.py scan --days 3 --max-results 50

# List all pending follow-ups from local tracker
python3 scripts/followup_reminder.py list-pending

# Mark a follow-up as resolved
python3 scripts/followup_reminder.py mark-resolved --thread-id THREAD_ID

# Add a manual follow-up reminder
python3 scripts/followup_reminder.py add-manual --subject "Invoice payment" --recipient "client@example.com" --days 5
```
