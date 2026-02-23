---
name: clerk-admin
version: 1.0.0
description: "OC-0059: Clerk User Admin - Ban/unban users, manage sessions and roles via the Clerk Backend API."
---

# Clerk User Admin

Manage Clerk users, sessions, and roles from the command line.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `CLERK_SECRET_KEY` environment variable set to your Clerk secret key

## Commands

| Command | Description |
|---------|-------------|
| `list-users` | List all users with optional limit |
| `get-user` | Get details for a specific user by ID |
| `ban` | Ban a user by ID |
| `unban` | Unban a previously banned user |
| `delete-user` | Permanently delete a user |
| `list-sessions` | List active sessions for a user |
| `update-role` | Update the role for a user in an organization |

## Usage

```bash
export CLERK_SECRET_KEY="sk_live_..."

python scripts/clerk_admin.py list-users --limit 10
python scripts/clerk_admin.py get-user --user-id user_abc123
python scripts/clerk_admin.py ban --user-id user_abc123
python scripts/clerk_admin.py unban --user-id user_abc123
python scripts/clerk_admin.py delete-user --user-id user_abc123
python scripts/clerk_admin.py list-sessions --user-id user_abc123
python scripts/clerk_admin.py update-role --user-id user_abc123 --org-id org_xyz --role admin
```
