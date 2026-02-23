---
name: neon-branch-manager
version: 1.0.0
description: Neon Branch Manager (OC-0025). Create instant Postgres branches for every PR. Use when user asks to manage Neon database branches, create dev branches, or list endpoints.
---

# Neon Branch Manager

Create and manage instant Postgres branches on Neon for every pull request or development environment.

## Capabilities

1. **List Branches**: View all branches in a Neon project.
2. **Create Branch**: Spin up an instant Postgres branch from any parent.
3. **Delete Branch**: Remove branches that are no longer needed.
4. **Get Branch**: Inspect details of a specific branch.
5. **List Endpoints**: View compute endpoints associated with branches.

## Quick Start

```bash
# List all branches
python3 skills/system-integrations/database-storage/neon-branch-manager/scripts/manage.py list-branches

# Create a branch for a PR
python3 skills/system-integrations/database-storage/neon-branch-manager/scripts/manage.py create-branch --name pr-42-preview

# Get branch details
python3 skills/system-integrations/database-storage/neon-branch-manager/scripts/manage.py get-branch --branch-id br-abc123

# Delete a branch
python3 skills/system-integrations/database-storage/neon-branch-manager/scripts/manage.py delete-branch --branch-id br-abc123

# List endpoints
python3 skills/system-integrations/database-storage/neon-branch-manager/scripts/manage.py list-endpoints
```

## Commands & Parameters

### `list-branches`
Lists all branches in the Neon project.
- No required parameters.

### `create-branch`
Creates a new database branch.
- `--name`: Name for the new branch (required).
- `--parent-id`: Parent branch ID (default: primary branch).

### `delete-branch`
Deletes a branch by ID.
- `--branch-id`: Branch ID to delete (required).

### `get-branch`
Gets details for a specific branch.
- `--branch-id`: Branch ID (required).

### `list-endpoints`
Lists compute endpoints for the project.
- No required parameters.

## Dependencies
- `NEON_API_KEY` environment variable (Neon API key).
- `NEON_PROJECT_ID` environment variable (Neon project ID).
- Python `requests` library (`pip install requests`).
