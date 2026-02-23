---
name: logrocket-finder
id: OC-0053
version: 1.0.0
description: "LogRocket Session Finder - Find user sessions with errors"
env:
  - LOGROCKET_APP_ID
  - LOGROCKET_API_KEY
commands:
  - list-sessions
  - search
  - get-session
  - list-errors
  - get-url
---

# LogRocket Session Finder

Search LogRocket sessions for user errors, replay URLs, and session details.

## Prerequisites

- `LOGROCKET_APP_ID` – LogRocket application ID.
- `LOGROCKET_API_KEY` – LogRocket API key.

## Commands

| Command         | Description                              |
|-----------------|------------------------------------------|
| `list-sessions` | List recent sessions                     |
| `search`        | Search sessions by email or user ID      |
| `get-session`   | Get details for a specific session       |
| `list-errors`   | List errors in a session                 |
| `get-url`       | Get the replay URL for a session         |

## Usage

```bash
export LOGROCKET_APP_ID="your-app-id"
export LOGROCKET_API_KEY="your-api-key"
python3 scripts/logrocket_finder.py list-sessions --limit 10
python3 scripts/logrocket_finder.py search --email user@example.com
python3 scripts/logrocket_finder.py get-session --session-id abc123
python3 scripts/logrocket_finder.py list-errors --session-id abc123
python3 scripts/logrocket_finder.py get-url --session-id abc123
```
