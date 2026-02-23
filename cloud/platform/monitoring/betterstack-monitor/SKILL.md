---
name: betterstack-monitor
id: OC-0057
version: 1.0.0
description: "Better Stack Monitor - Check uptime incidents"
env:
  - BETTERSTACK_API_TOKEN
commands:
  - list-monitors
  - get-monitor
  - list-incidents
  - acknowledge
  - resolve
---

# Better Stack Monitor

Monitor uptime, list incidents, acknowledge, and resolve via the Better Stack API.

## Prerequisites

- `BETTERSTACK_API_TOKEN` – Better Stack API token.

## Commands

| Command          | Description                              |
|------------------|------------------------------------------|
| `list-monitors`  | List all uptime monitors                 |
| `get-monitor`    | Get details for a specific monitor       |
| `list-incidents` | List recent incidents                    |
| `acknowledge`    | Acknowledge an incident                  |
| `resolve`        | Resolve an incident                      |

## Usage

```bash
export BETTERSTACK_API_TOKEN="your-token"
python3 scripts/betterstack_monitor.py list-monitors
python3 scripts/betterstack_monitor.py get-monitor --monitor-id 12345
python3 scripts/betterstack_monitor.py list-incidents
python3 scripts/betterstack_monitor.py acknowledge --incident-id 67890
python3 scripts/betterstack_monitor.py resolve --incident-id 67890
```
