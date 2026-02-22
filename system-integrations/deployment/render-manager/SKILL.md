---
name: render-manager
id: OC-0012
version: 1.0.0
description: "Render Service Manager - Scale services up/down"
env:
  - RENDER_API_KEY
commands:
  - list-services
  - get-service
  - scale
  - restart
  - get-deploys
---

# Render Service Manager

Manage Render services, scaling, restarts, and deployments.

## Prerequisites

- A valid `RENDER_API_KEY` environment variable.

## Commands

| Command         | Description                        |
|-----------------|------------------------------------|
| `list-services` | List all Render services           |
| `get-service`   | Get details of a specific service  |
| `scale`         | Scale a service instance count     |
| `restart`       | Restart a service                  |
| `get-deploys`   | List recent deploys for a service  |

## Usage

```bash
export RENDER_API_KEY="your-key"
python3 scripts/render_manager.py list-services
python3 scripts/render_manager.py scale --service-id srv-xxx --num-instances 3
python3 scripts/render_manager.py restart --service-id srv-xxx
```
