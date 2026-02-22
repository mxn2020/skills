---
name: flyio-manager
id: OC-0023
version: 1.0.0
description: "Fly.io App Manager - Deploy and scale apps globally"
env: []
commands:
  - list-apps
  - deploy
  - scale
  - get-status
  - list-regions
---

# Fly.io App Manager

Deploy, scale, and manage Fly.io applications across global regions.

## Prerequisites

- `flyctl` CLI installed and authenticated (`fly auth login`).

## Commands

| Command        | Description                          |
|----------------|--------------------------------------|
| `list-apps`    | List all Fly.io apps                 |
| `deploy`       | Deploy the current app               |
| `scale`        | Scale VM count/size                  |
| `get-status`   | Get app status and allocations       |
| `list-regions` | List available Fly.io regions        |

## Usage

```bash
python3 scripts/flyio_manager.py list-apps
python3 scripts/flyio_manager.py deploy --app my-app
python3 scripts/flyio_manager.py scale --app my-app --count 3 --vm-size shared-cpu-1x
```
