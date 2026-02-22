---
name: planetscale-inspector
version: 1.0.0
description: PlanetScale Schema Inspector (OC-0028). Check migrations and schema diffs on PlanetScale. Use when user asks to inspect PlanetScale schemas, branches, or deploy requests.
---

# PlanetScale Schema Inspector

Check migrations and schema diffs on PlanetScale MySQL databases.

## Capabilities

1. **List Databases**: View all databases in the organization.
2. **List Branches**: View database branches.
3. **Get Schema**: Retrieve the schema for a branch.
4. **Create Deploy Request**: Open a deploy request for schema changes.
5. **Diff**: Compare schemas between two branches.

## Quick Start

```bash
# List databases
python3 skills/system-integrations/database-storage/planetscale-inspector/scripts/manage.py list-databases

# List branches
python3 skills/system-integrations/database-storage/planetscale-inspector/scripts/manage.py list-branches --database mydb

# Get schema
python3 skills/system-integrations/database-storage/planetscale-inspector/scripts/manage.py get-schema --database mydb --branch main

# Create a deploy request
python3 skills/system-integrations/database-storage/planetscale-inspector/scripts/manage.py create-deploy-request --database mydb --branch feature-xyz --into main

# Diff branches
python3 skills/system-integrations/database-storage/planetscale-inspector/scripts/manage.py diff --database mydb --branch feature-xyz --base main
```

## Commands & Parameters

### `list-databases`
Lists all databases in the organization.
- No required parameters.

### `list-branches`
Lists branches for a database.
- `--database`: Database name (required).

### `get-schema`
Gets the schema for a branch.
- `--database`: Database name (required).
- `--branch`: Branch name (required).

### `create-deploy-request`
Creates a deploy request.
- `--database`: Database name (required).
- `--branch`: Source branch (required).
- `--into`: Target branch (required).

### `diff`
Shows schema diff between two branches.
- `--database`: Database name (required).
- `--branch`: Source branch (required).
- `--base`: Base branch to compare against (required).

## Dependencies
- `PLANETSCALE_TOKEN` environment variable (PlanetScale service token).
- `PLANETSCALE_ORG` environment variable (organization name).
- Python `requests` library (`pip install requests`).
