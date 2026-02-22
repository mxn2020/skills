---
name: firebase-auth
version: 1.0.0
description: "OC-0063: Firebase Auth Manager - Disable accounts, revoke tokens, and manage custom claims via the Firebase Auth REST API."
---

# Firebase Auth Manager

Manage Firebase Auth users, disable accounts, and set custom claims from the CLI.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `FIREBASE_PROJECT_ID` environment variable set to your Firebase project ID
- `GOOGLE_APPLICATION_CREDENTIALS` environment variable pointing to a service account JSON file

## Commands

| Command | Description |
|---------|-------------|
| `list-users` | List all users with pagination |
| `get-user` | Get details for a specific user by UID |
| `create-user` | Create a new user with email and password |
| `disable-user` | Disable a user account |
| `delete-user` | Permanently delete a user |
| `set-claims` | Set custom claims on a user |

## Usage

```bash
export FIREBASE_PROJECT_ID="my-project"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"

python scripts/firebase_auth.py list-users --limit 20
python scripts/firebase_auth.py get-user --uid "abc123"
python scripts/firebase_auth.py create-user --email user@example.com --password "s3cret!"
python scripts/firebase_auth.py disable-user --uid "abc123"
python scripts/firebase_auth.py delete-user --uid "abc123"
python scripts/firebase_auth.py set-claims --uid "abc123" --claims '{"admin": true}'
```
