---
name: upstash-redis
version: 1.0.0
description: Upstash Redis CLI (OC-0030). Use serverless Redis for key-value jobs. Use when user asks to get, set, or manage keys in Upstash Redis.
---

# Upstash Redis CLI

Use serverless Redis for key-value operations via the Upstash REST API.

## Capabilities

1. **Get**: Retrieve a value by key.
2. **Set**: Store a key-value pair.
3. **Del**: Delete a key.
4. **Keys**: List keys matching a pattern.
5. **Info**: Get server information.
6. **TTL**: Check time-to-live of a key.
7. **Expire**: Set expiration on a key.

## Quick Start

```bash
# Set a key
python3 skills/cloud/data/databases/upstash-redis/scripts/manage.py set --key mykey --value "hello world"

# Get a key
python3 skills/cloud/data/databases/upstash-redis/scripts/manage.py get --key mykey

# List keys
python3 skills/cloud/data/databases/upstash-redis/scripts/manage.py keys --pattern "user:*"

# Set TTL
python3 skills/cloud/data/databases/upstash-redis/scripts/manage.py expire --key mykey --seconds 3600

# Check TTL
python3 skills/cloud/data/databases/upstash-redis/scripts/manage.py ttl --key mykey

# Delete a key
python3 skills/cloud/data/databases/upstash-redis/scripts/manage.py del --key mykey

# Server info
python3 skills/cloud/data/databases/upstash-redis/scripts/manage.py info
```

## Commands & Parameters

### `get`
Gets the value of a key.
- `--key`: Key name (required).

### `set`
Sets a key-value pair.
- `--key`: Key name (required).
- `--value`: Value to store (required).
- `--ex`: Expiration in seconds (optional).

### `del`
Deletes a key.
- `--key`: Key name (required).

### `keys`
Lists keys matching a pattern.
- `--pattern`: Glob pattern (default: *).

### `info`
Returns server information.
- No required parameters.

### `ttl`
Gets the TTL of a key in seconds.
- `--key`: Key name (required).

### `expire`
Sets expiration on a key.
- `--key`: Key name (required).
- `--seconds`: TTL in seconds (required).

## Dependencies
- `UPSTASH_REDIS_URL` environment variable (Upstash Redis REST URL).
- `UPSTASH_REDIS_TOKEN` environment variable (Upstash Redis REST token).
- Python `requests` library (`pip install requests`).
