---
name: dynamodb-browser
version: 1.0.0
description: DynamoDB Item Browser (OC-0032). Query NoSQL data efficiently using the AWS CLI. Use when user asks to browse, query, or manage items in DynamoDB tables.
---

# DynamoDB Item Browser

Query and manage NoSQL data in AWS DynamoDB efficiently using the AWS CLI.

## Capabilities

1. **List Tables**: View all DynamoDB tables.
2. **Scan**: Scan a table for items.
3. **Query**: Query items by partition key.
4. **Get Item**: Retrieve a specific item by key.
5. **Put Item**: Write an item to a table.
6. **Delete Item**: Remove an item by key.

## Quick Start

```bash
# List tables
python3 skills/system-integrations/database-storage/dynamodb-browser/scripts/manage.py list-tables

# Scan a table
python3 skills/system-integrations/database-storage/dynamodb-browser/scripts/manage.py scan --table Users --limit 10

# Query by partition key
python3 skills/system-integrations/database-storage/dynamodb-browser/scripts/manage.py query --table Users --key-condition "userId = :uid" --values '{":uid":{"S":"user-123"}}'

# Get a specific item
python3 skills/system-integrations/database-storage/dynamodb-browser/scripts/manage.py get-item --table Users --key '{"userId":{"S":"user-123"}}'

# Put an item
python3 skills/system-integrations/database-storage/dynamodb-browser/scripts/manage.py put-item --table Users --item '{"userId":{"S":"user-456"},"name":{"S":"Alice"}}'

# Delete an item
python3 skills/system-integrations/database-storage/dynamodb-browser/scripts/manage.py delete-item --table Users --key '{"userId":{"S":"user-123"}}'
```

## Commands & Parameters

### `list-tables`
Lists all DynamoDB tables in the account.
- `--region`: AWS region (optional, uses default).

### `scan`
Scans a table.
- `--table`: Table name (required).
- `--limit`: Max items (default: 25).
- `--region`: AWS region (optional).

### `query`
Queries items by key condition.
- `--table`: Table name (required).
- `--key-condition`: Key condition expression (required).
- `--values`: Expression attribute values as JSON (required).
- `--region`: AWS region (optional).

### `get-item`
Gets a single item by key.
- `--table`: Table name (required).
- `--key`: Key as JSON (required).
- `--region`: AWS region (optional).

### `put-item`
Writes an item to a table.
- `--table`: Table name (required).
- `--item`: Item as JSON (required).
- `--region`: AWS region (optional).

### `delete-item`
Deletes an item by key.
- `--table`: Table name (required).
- `--key`: Key as JSON (required).
- `--region`: AWS region (optional).

## Dependencies
- AWS CLI v2 installed and configured (`aws configure`).
- Appropriate IAM permissions for DynamoDB operations.
