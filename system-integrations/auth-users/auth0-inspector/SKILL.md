---
name: auth0-inspector
version: 1.0.0
description: "OC-0060: Auth0 Log Inspector - Check failed login attempts and anomalies via the Auth0 Management API."
---

# Auth0 Log Inspector

Inspect Auth0 logs for failed logins, anomalies, and manage users and connections.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `AUTH0_DOMAIN` environment variable (e.g. `your-tenant.us.auth0.com`)
- `AUTH0_MGMT_TOKEN` environment variable set to a Management API token

## Commands

| Command | Description |
|---------|-------------|
| `list-logs` | List recent log events |
| `search-logs` | Search logs with a Lucene query |
| `list-users` | List all users |
| `get-user` | Get details for a specific user |
| `block-user` | Block a user by ID |
| `list-connections` | List configured identity connections |

## Usage

```bash
export AUTH0_DOMAIN="your-tenant.us.auth0.com"
export AUTH0_MGMT_TOKEN="eyJ..."

python scripts/auth0_inspector.py list-logs --limit 25
python scripts/auth0_inspector.py search-logs --query "type:f"
python scripts/auth0_inspector.py list-users --limit 10
python scripts/auth0_inspector.py get-user --user-id "auth0|abc123"
python scripts/auth0_inspector.py block-user --user-id "auth0|abc123"
python scripts/auth0_inspector.py list-connections
```
