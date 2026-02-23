---
name: outlook-manager
id: OC-0138
version: 1.0.0
description: "Outlook Mail Manager - Manage emails and calendar within Microsoft 365"
env:
  - OUTLOOK_TOKEN
commands:
  - list-unread
  - send-email
  - reply
  - move-to-folder
  - list-folders
  - search
---

# Outlook Mail Manager

Manage Microsoft 365 emails and calendar events from the terminal via Microsoft Graph API.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `OUTLOOK_TOKEN` — OAuth 2.0 bearer token with `Mail.ReadWrite`, `Mail.Send` scopes

## Commands

| Command | Description |
|---------|-------------|
| `list-unread` | List unread emails |
| `send-email` | Send a new email |
| `reply` | Reply to an email |
| `move-to-folder` | Move email to a folder |
| `list-folders` | List all mail folders |
| `search` | Search emails by keyword |

## Usage

```bash
export OUTLOOK_TOKEN="your_graph_api_token"

# List up to 20 unread emails
python3 scripts/outlook_manager.py list-unread --top 20

# Send an email
python3 scripts/outlook_manager.py send-email --to "user@example.com" --subject "Hello" --body "Hi there!"

# Reply to an email
python3 scripts/outlook_manager.py reply --message-id MESSAGE_ID --body "Thanks for reaching out."

# Move email to a folder
python3 scripts/outlook_manager.py move-to-folder --message-id MESSAGE_ID --folder "Archive"

# List all mail folders
python3 scripts/outlook_manager.py list-folders

# Search emails
python3 scripts/outlook_manager.py search --query "invoice" --top 10
```
