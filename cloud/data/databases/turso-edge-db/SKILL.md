---
name: turso-edge-db
version: 1.0.0
description: Turso Edge DB Manager (OC-0036). Manage SQLite at the edge with Turso. Use when user asks to create, manage, or query Turso databases.
---

# Turso Edge DB Manager

Manage SQLite databases at the edge using the Turso Platform API.

## Capabilities

1. **List Databases**: View all databases in the organization.
2. **Create DB**: Create a new edge database.
3. **Delete DB**: Remove a database.
4. **Shell**: Execute SQL against a database.
5. **Get Stats**: View usage statistics for a database.

## Quick Start

```bash
# List databases
python3 skills/cloud/data/databases/turso-edge-db/scripts/manage.py list-databases

# Create a database
python3 skills/cloud/data/databases/turso-edge-db/scripts/manage.py create-db --name my-edge-db --group default

# Execute SQL
python3 skills/cloud/data/databases/turso-edge-db/scripts/manage.py shell --database my-edge-db --sql "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)"

# Get stats
python3 skills/cloud/data/databases/turso-edge-db/scripts/manage.py get-stats --database my-edge-db

# Delete a database
python3 skills/cloud/data/databases/turso-edge-db/scripts/manage.py delete-db --database my-edge-db
```

## Commands & Parameters

### `list-databases`
Lists all databases in the organization.
- No required parameters.

### `create-db`
Creates a new database.
- `--name`: Database name (required).
- `--group`: Group name (default: default).

### `delete-db`
Deletes a database.
- `--database`: Database name (required).

### `shell`
Executes SQL against a database.
- `--database`: Database name (required).
- `--sql`: SQL statement to execute (required).

### `get-stats`
Gets usage statistics for a database.
- `--database`: Database name (required).

## Dependencies
- `TURSO_TOKEN` environment variable (Turso API token).
- `TURSO_ORG` environment variable (organization slug).
- Python `requests` library (`pip install requests`).
