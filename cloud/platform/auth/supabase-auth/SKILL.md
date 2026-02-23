---
name: supabase-auth
version: 1.0.0
description: "OC-0061: Supabase Auth Helper - Send password reset emails, manage providers and users via the Supabase Admin API."
---

# Supabase Auth Helper

Manage Supabase Auth users, send password resets, and inspect MFA factors.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `SUPABASE_URL` environment variable (e.g. `https://xyzproject.supabase.co`)
- `SUPABASE_SERVICE_KEY` environment variable set to your service role key

## Commands

| Command | Description |
|---------|-------------|
| `list-users` | List all users with pagination |
| `get-user` | Get details for a specific user |
| `create-user` | Create a new user with email and password |
| `delete-user` | Delete a user by ID |
| `send-reset` | Send a password reset email to a user |
| `list-factors` | List MFA factors for a user |

## Usage

```bash
export SUPABASE_URL="https://xyzproject.supabase.co"
export SUPABASE_SERVICE_KEY="eyJ..."

python scripts/supabase_auth.py list-users --limit 20
python scripts/supabase_auth.py get-user --user-id "uuid-here"
python scripts/supabase_auth.py create-user --email user@example.com --password "s3cret!"
python scripts/supabase_auth.py delete-user --user-id "uuid-here"
python scripts/supabase_auth.py send-reset --email user@example.com
python scripts/supabase_auth.py list-factors --user-id "uuid-here"
```
