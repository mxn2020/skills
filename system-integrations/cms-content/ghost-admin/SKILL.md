---
name: Ghost Admin
id: OC-0047
version: 1.0.0
description: Manage membership tiers and posts via the Ghost Admin API.
---

# Ghost Admin

Create, update, and delete posts, and inspect membership tiers and members through the Ghost Admin API.

## Capabilities

- Full CRUD for Ghost posts (draft and published)
- List membership tiers and active members
- JWT-based Admin API authentication

## Quick Start

```bash
export GHOST_URL="https://your-ghost.example.com"
export GHOST_ADMIN_KEY="admin-api-key-id:secret"
python3 scripts/ghost_admin.py list-posts
python3 scripts/ghost_admin.py create-post --title "New Post" --html "<p>Content here</p>"
```

## Commands & Parameters

| Command        | Parameters                                          | Description                     |
| -------------- | --------------------------------------------------- | ------------------------------- |
| `list-posts`   | —                                                   | List recent posts               |
| `create-post`  | `--title`, `--html`, `--status` (default: draft)    | Create a new post               |
| `update-post`  | `--id`, `--title`/`--html`/`--status` (optional)    | Update an existing post         |
| `delete-post`  | `--id`                                              | Delete a post                   |
| `list-tiers`   | —                                                   | List membership tiers           |
| `list-members` | —                                                   | List members                    |

## Dependencies

- Python 3.8+
- `requests`, `PyJWT` libraries
- Environment variables: `GHOST_URL`, `GHOST_ADMIN_KEY`
