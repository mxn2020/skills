---
name: workos-directory
version: 1.0.0
description: "OC-0062: WorkOS Directory Sync - Manage enterprise SSO and SCIM directories via the WorkOS API."
---

# WorkOS Directory Sync

Manage enterprise directory sync, SSO connections, and organizations via WorkOS.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `WORKOS_API_KEY` environment variable set to your WorkOS API key

## Commands

| Command | Description |
|---------|-------------|
| `list-directories` | List all configured directories |
| `list-users` | List users in a directory |
| `list-groups` | List groups in a directory |
| `get-directory` | Get details of a specific directory |
| `list-connections` | List SSO connections |
| `list-orgs` | List organizations |

## Usage

```bash
export WORKOS_API_KEY="sk_live_..."

python scripts/workos_directory.py list-directories --limit 10
python scripts/workos_directory.py list-users --directory-id dir_abc123
python scripts/workos_directory.py list-groups --directory-id dir_abc123
python scripts/workos_directory.py get-directory --directory-id dir_abc123
python scripts/workos_directory.py list-connections --limit 10
python scripts/workos_directory.py list-orgs --limit 10
```
