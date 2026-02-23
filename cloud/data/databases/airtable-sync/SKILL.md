---
name: airtable-sync
version: 1.0.0
description: Airtable Record Sync (OC-0034). Treat Airtable as a lightweight CMS/DB. Use when user asks to list, create, update, or delete records in Airtable.
---

# Airtable Record Sync

Treat Airtable as a lightweight CMS/DB for managing structured records.

## Capabilities

1. **List Bases**: View accessible Airtable bases.
2. **List Records**: Browse records in a table.
3. **Create Record**: Add a new record to a table.
4. **Update Record**: Modify an existing record.
5. **Delete Record**: Remove a record.

## Quick Start

```bash
# List bases
python3 skills/cloud/data/databases/airtable-sync/scripts/manage.py list-bases

# List records
python3 skills/cloud/data/databases/airtable-sync/scripts/manage.py list-records --table Tasks --max-records 10

# Create a record
python3 skills/cloud/data/databases/airtable-sync/scripts/manage.py create-record --table Tasks --fields '{"Name":"Fix bug","Status":"Todo"}'

# Update a record
python3 skills/cloud/data/databases/airtable-sync/scripts/manage.py update-record --table Tasks --record-id rec123 --fields '{"Status":"Done"}'

# Delete a record
python3 skills/cloud/data/databases/airtable-sync/scripts/manage.py delete-record --table Tasks --record-id rec123
```

## Commands & Parameters

### `list-bases`
Lists all accessible Airtable bases.
- No required parameters.

### `list-records`
Lists records in a table.
- `--table`: Table name (required).
- `--view`: View name (optional).
- `--max-records`: Max records to return (default: 50).
- `--formula`: Filter formula (optional).

### `create-record`
Creates a new record.
- `--table`: Table name (required).
- `--fields`: JSON object with field values (required).

### `update-record`
Updates an existing record.
- `--table`: Table name (required).
- `--record-id`: Record ID (required).
- `--fields`: JSON object with updated field values (required).

### `delete-record`
Deletes a record.
- `--table`: Table name (required).
- `--record-id`: Record ID (required).

## Dependencies
- `AIRTABLE_API_KEY` environment variable (Airtable personal access token).
- `AIRTABLE_BASE_ID` environment variable (base ID, e.g., appXXXXXXXXXXXX).
- Python `requests` library (`pip install requests`).
