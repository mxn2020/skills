---
name: novu-notifications
id: OC-0081
version: 1.0.0
description: "Novu Notification Manager – Trigger and manage in-app, email, and push notifications"
env:
  - NOVU_API_KEY
commands:
  - trigger
  - list-subscribers
  - create-subscriber
  - list-notifications
  - list-topics
---

# Novu Notification Manager

Trigger and manage in-app, email, and push notifications via the Novu platform.

## Prerequisites

- `NOVU_API_KEY` – Novu API key.

## Commands

| Command              | Description                              |
|----------------------|------------------------------------------|
| `trigger`            | Trigger a notification workflow          |
| `list-subscribers`   | List subscribers                         |
| `create-subscriber`  | Create a new subscriber                  |
| `list-notifications` | List sent notifications                  |
| `list-topics`        | List notification topics                 |

## Usage

```bash
export NOVU_API_KEY="your-api-key"
python3 scripts/novu_notifications.py trigger --workflow my-workflow --subscriber-id user123 --payload '{"message": "Hello"}'
python3 scripts/novu_notifications.py list-subscribers --page 0
python3 scripts/novu_notifications.py create-subscriber --subscriber-id user456 --email user@example.com --first-name Jane --last-name Doe
python3 scripts/novu_notifications.py list-notifications --page 0
python3 scripts/novu_notifications.py list-topics --page 0
```
