---
name: cockroachdb-runner
version: 1.0.0
description: CockroachDB Query Runner (OC-0035). Execute distributed SQL queries on CockroachDB. Use when user asks to run SQL, list databases, or describe tables in CockroachDB.
---

# CockroachDB Query Runner

Execute distributed SQL queries on CockroachDB clusters.

## Capabilities

1. **Query**: Run a SELECT query and display results.
2. **List Databases**: Show all databases.
3. **List Tables**: Show tables in a database.
4. **Describe**: Describe a table schema.
5. **Execute**: Run DDL/DML statements (INSERT, UPDATE, CREATE, etc.).

## Quick Start

```bash
# List databases
python3 skills/cloud/data/databases/cockroachdb-runner/scripts/manage.py list-databases

# List tables
python3 skills/cloud/data/databases/cockroachdb-runner/scripts/manage.py list-tables --database defaultdb

# Describe a table
python3 skills/cloud/data/databases/cockroachdb-runner/scripts/manage.py describe --table users

# Run a query
python3 skills/cloud/data/databases/cockroachdb-runner/scripts/manage.py query --sql "SELECT * FROM users LIMIT 10"

# Execute a statement
python3 skills/cloud/data/databases/cockroachdb-runner/scripts/manage.py execute --sql "INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')"
```

## Commands & Parameters

### `query`
Runs a SELECT query.
- `--sql`: SQL query string (required).

### `list-databases`
Lists all databases.
- No required parameters.

### `list-tables`
Lists tables in a database.
- `--database`: Database name (default: defaultdb).

### `describe`
Describes a table schema.
- `--table`: Table name (required).

### `execute`
Executes a DDL/DML statement.
- `--sql`: SQL statement (required).

## Dependencies
- `COCKROACH_URL` environment variable (CockroachDB connection string, e.g., `postgresql://user:pass@host:26257/defaultdb?sslmode=verify-full`).
- Python `psycopg2` library (`pip install psycopg2-binary`).
