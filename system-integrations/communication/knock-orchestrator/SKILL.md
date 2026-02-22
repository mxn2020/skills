---
name: knock-orchestrator
id: OC-0080
version: 1.0.0
description: "Knock Notification Orchestrator - Manage multi-channel notification workflows"
env:
  - KNOCK_API_KEY
commands:
  - trigger-workflow
  - list-workflows
  - get-message
  - list-messages
  - identify-user
---

# Knock Notification Orchestrator

Manage multi-channel notification workflows, trigger notifications, inspect messages, and identify users via the Knock API.

## Prerequisites

- `KNOCK_API_KEY` – Knock API secret key.

## Commands

| Command            | Description                                  |
|--------------------|----------------------------------------------|
| `trigger-workflow` | Trigger a notification workflow for recipients |
| `list-workflows`   | List available notification workflows        |
| `get-message`      | Get details for a specific message           |
| `list-messages`    | List messages with optional status filter    |
| `identify-user`    | Identify or create a user in Knock           |

## Usage

```bash
export KNOCK_API_KEY="your-key"
python3 scripts/knock_orchestrator.py trigger-workflow --workflow-key welcome --recipients user-1 user-2 --data '{"message": "hello"}'
python3 scripts/knock_orchestrator.py list-workflows
python3 scripts/knock_orchestrator.py get-message --message-id msg_123
python3 scripts/knock_orchestrator.py list-messages --status delivered
python3 scripts/knock_orchestrator.py identify-user --user-id user-1 --name "Jane Doe" --email jane@example.com
```
