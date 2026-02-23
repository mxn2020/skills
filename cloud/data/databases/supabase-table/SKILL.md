---
name: supabase-table
version: 1.0.0
description: Supabase Table Editor (OC-0027). Run safe read/write operations on Supabase tables. Use when user asks to query, insert, update, or delete rows in Supabase.
---

# Supabase Table Editor

Run safe read/write operations on Supabase Postgres tables via the REST API.

## Capabilities

1. **List Tables**: View all tables in the database.
2. **Query**: Read rows with filters and ordering.
3. **Insert**: Add new rows to a table.
4. **Update**: Modify existing rows with filters.
5. **Delete**: Remove rows matching a filter.

## Quick Start

```bash
# List all tables
python3 skills/cloud/data/databases/supabase-table/scripts/manage.py list-tables

# Query rows
python3 skills/cloud/data/databases/supabase-table/scripts/manage.py query --table users --select "id,name,email" --filter "status=eq.active" --limit 10

# Insert a row
python3 skills/cloud/data/databases/supabase-table/scripts/manage.py insert --table users --data '{"name":"Alice","email":"alice@example.com"}'

# Update rows
python3 skills/cloud/data/databases/supabase-table/scripts/manage.py update --table users --filter "id=eq.5" --data '{"status":"inactive"}'

# Delete rows
python3 skills/cloud/data/databases/supabase-table/scripts/manage.py delete --table users --filter "status=eq.inactive"
```

## Commands & Parameters

### `list-tables`
Lists all tables in the public schema.
- No required parameters.

### `query`
Reads rows from a table.
- `--table`: Table name (required).
- `--select`: Columns to select (default: *).
- `--filter`: PostgREST filter (e.g., status=eq.active).
- `--order`: Order by column (e.g., created_at.desc).
- `--limit`: Max rows (default: 50).

### `insert`
Inserts a row into a table.
- `--table`: Table name (required).
- `--data`: JSON object with column values (required).

### `update`
Updates rows matching a filter.
- `--table`: Table name (required).
- `--filter`: PostgREST filter to match rows (required).
- `--data`: JSON object with updated values (required).

### `delete`
Deletes rows matching a filter.
- `--table`: Table name (required).
- `--filter`: PostgREST filter to match rows (required).

## Dependencies
- `SUPABASE_URL` environment variable (Supabase project URL).
- `SUPABASE_SERVICE_KEY` environment variable (service role key).
- Python `requests` library (`pip install requests`).
