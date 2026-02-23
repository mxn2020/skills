---
name: heroku-scaler
id: OC-0020
version: 1.0.0
description: "Heroku Dyno Scaler - Adjust resources dynamically"
env:
  - HEROKU_API_KEY
commands:
  - list-apps
  - scale
  - restart
  - get-logs
  - list-dynos
---

# Heroku Dyno Scaler

Manage Heroku apps, scale dynos, restart, and fetch logs.

## Prerequisites

- `HEROKU_API_KEY` environment variable or `heroku` CLI authenticated.

## Commands

| Command       | Description                          |
|---------------|--------------------------------------|
| `list-apps`   | List all Heroku apps                 |
| `scale`       | Scale dynos for an app               |
| `restart`     | Restart app dynos                    |
| `get-logs`    | Fetch recent app logs                |
| `list-dynos`  | List running dynos                   |

## Usage

```bash
export HEROKU_API_KEY="your-key"
python3 scripts/heroku_scaler.py list-apps
python3 scripts/heroku_scaler.py scale --app my-app --type web --qty 2
python3 scripts/heroku_scaler.py get-logs --app my-app --lines 100
```
