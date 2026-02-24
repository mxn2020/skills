---
name: docker-compose-wizard
id: OC-0192
version: 1.0.0
description: "Scaffold multi-container development environments from natural language descriptions."
env:
  - OPENAI_API_KEY
commands:
  - generate-compose
  - validate
---

# Docker Compose Wizard

Scaffold multi-container development environments from natural language descriptions.

## Prerequisites
- A valid `OPENAI_API_KEY` environment variable.

## Commands
| Command            | Description                              |
|--------------------|------------------------------------------|
| `generate-compose` | Generate `docker-compose.yml` based on architecture request |
| `validate`         | Run a check against the generated compose file |

## Usage
```bash
export OPENAI_API_KEY="sk-..."
python3 scripts/docker_compose_wizard.py generate-compose --prompt "A Node.js backend using PM2, an Nginx reverse proxy, and a Postgres database."
python3 scripts/docker_compose_wizard.py validate --file docker-compose.yml
```
