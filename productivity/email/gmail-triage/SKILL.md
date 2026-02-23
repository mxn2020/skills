---
name: gmail-triage
id: OC-0137
version: 1.0.0
description: "Gmail Inbox Triage - Summarize, label, and draft replies to unread emails"
env:
  - GMAIL_TOKEN
commands:
  - list-unread
  - summarize
  - label
  - archive
  - draft-reply
---

# Gmail Inbox Triage

Manage your Gmail inbox from the terminal: list unread emails, auto-summarize threads, add labels, archive, and draft AI-powered replies.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `GMAIL_TOKEN` — OAuth 2.0 bearer token with `gmail.modify` scope

## Commands

| Command | Description |
|---------|-------------|
| `list-unread` | List unread emails in inbox |
| `summarize` | Summarize a specific email thread |
| `label` | Add a label to an email |
| `archive` | Archive (remove from inbox) an email |
| `draft-reply` | Generate and save a draft reply |

## Usage

```bash
export GMAIL_TOKEN="your_oauth_token"

# List up to 20 unread emails
python3 scripts/gmail_triage.py list-unread --max-results 20

# Summarize a thread
python3 scripts/gmail_triage.py summarize --message-id MESSAGE_ID

# Add a label to an email
python3 scripts/gmail_triage.py label --message-id MESSAGE_ID --label-name "Follow Up"

# Archive an email
python3 scripts/gmail_triage.py archive --message-id MESSAGE_ID

# Generate a draft reply
python3 scripts/gmail_triage.py draft-reply --message-id MESSAGE_ID --tone "professional"
```
