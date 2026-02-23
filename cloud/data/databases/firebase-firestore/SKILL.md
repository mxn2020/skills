---
name: firebase-firestore
version: 1.0.0
description: Firebase Firestore Admin (OC-0033). Read/Write Firestore documents. Use when user asks to manage Firestore collections, documents, or queries.
---

# Firebase Firestore Admin

Read and write documents in Google Cloud Firestore via the REST API.

## Capabilities

1. **List Collections**: View top-level collections.
2. **Get Document**: Read a specific document.
3. **Set Document**: Create or overwrite a document.
4. **Delete Document**: Remove a document.
5. **Query**: Query documents in a collection with filters.

## Quick Start

```bash
# List collections
python3 skills/cloud/data/databases/firebase-firestore/scripts/manage.py list-collections --project my-project

# Get a document
python3 skills/cloud/data/databases/firebase-firestore/scripts/manage.py get-doc --project my-project --collection users --doc user-123

# Set a document
python3 skills/cloud/data/databases/firebase-firestore/scripts/manage.py set-doc --project my-project --collection users --doc user-456 --data '{"name":"Alice","role":"admin"}'

# Delete a document
python3 skills/cloud/data/databases/firebase-firestore/scripts/manage.py delete-doc --project my-project --collection users --doc user-123

# Query a collection
python3 skills/cloud/data/databases/firebase-firestore/scripts/manage.py query --project my-project --collection users --field role --op EQUAL --value admin
```

## Commands & Parameters

### `list-collections`
Lists top-level collections.
- `--project`: GCP project ID (required).

### `get-doc`
Gets a document by path.
- `--project`: GCP project ID (required).
- `--collection`: Collection name (required).
- `--doc`: Document ID (required).

### `set-doc`
Creates or overwrites a document.
- `--project`: GCP project ID (required).
- `--collection`: Collection name (required).
- `--doc`: Document ID (required).
- `--data`: JSON data for the document (required).

### `delete-doc`
Deletes a document.
- `--project`: GCP project ID (required).
- `--collection`: Collection name (required).
- `--doc`: Document ID (required).

### `query`
Queries a collection.
- `--project`: GCP project ID (required).
- `--collection`: Collection name (required).
- `--field`: Field to filter on (required).
- `--op`: Comparison operator (EQUAL, LESS_THAN, GREATER_THAN, etc.) (required).
- `--value`: Filter value (required).
- `--limit`: Max results (default: 20).

## Dependencies
- `GOOGLE_APPLICATION_CREDENTIALS` environment variable (path to service account JSON).
- Python `requests` library (`pip install requests`).
