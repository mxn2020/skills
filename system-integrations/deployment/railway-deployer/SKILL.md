---
name: railway-deployer
id: OC-0011
version: 1.0.0
description: "Railway Project Deployer - Spin up new service instances"
env:
  - RAILWAY_TOKEN
commands:
  - list-projects
  - deploy
  - list-services
  - get-logs
  - set-variable
---

# Railway Project Deployer

Manage Railway projects, services, deployments, and environment variables.

## Prerequisites

- A valid `RAILWAY_TOKEN` environment variable.

## Commands

| Command          | Description                        |
|------------------|------------------------------------|
| `list-projects`  | List all Railway projects          |
| `deploy`         | Trigger a new deployment           |
| `list-services`  | List services in a project         |
| `get-logs`       | Fetch deployment logs              |
| `set-variable`   | Set an environment variable        |

## Usage

```bash
export RAILWAY_TOKEN="your-token"
python3 scripts/railway_deployer.py list-projects
python3 scripts/railway_deployer.py deploy --project-id xxx --service-id yyy
python3 scripts/railway_deployer.py set-variable --project-id xxx --name KEY --value val
```
