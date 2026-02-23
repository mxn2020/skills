---
name: supabase-bucket
version: 1.0.0
description: Supabase Bucket Manager (OC-0026). Manage heavy media assets in Supabase Storage. Use when user asks to upload, download, or manage files in Supabase buckets.
---

# Supabase Bucket Manager

Manage heavy media assets in Supabase Storage buckets.

## Capabilities

1. **List Buckets**: View all storage buckets in a project.
2. **Create Bucket**: Create a new storage bucket.
3. **List Files**: Browse files in a bucket.
4. **Upload**: Upload files to a bucket.
5. **Download**: Download files from a bucket.
6. **Delete File**: Remove files from a bucket.

## Quick Start

```bash
# List all buckets
python3 skills/cloud/data/databases/supabase-bucket/scripts/manage.py list-buckets

# Create a new bucket
python3 skills/cloud/data/databases/supabase-bucket/scripts/manage.py create-bucket --name media-assets --public

# List files in a bucket
python3 skills/cloud/data/databases/supabase-bucket/scripts/manage.py list-files --bucket media-assets

# Upload a file
python3 skills/cloud/data/databases/supabase-bucket/scripts/manage.py upload --bucket media-assets --file ./image.png --path uploads/image.png

# Download a file
python3 skills/cloud/data/databases/supabase-bucket/scripts/manage.py download --bucket media-assets --path uploads/image.png --output ./downloaded.png

# Delete a file
python3 skills/cloud/data/databases/supabase-bucket/scripts/manage.py delete-file --bucket media-assets --path uploads/image.png
```

## Commands & Parameters

### `list-buckets`
Lists all storage buckets.
- No required parameters.

### `create-bucket`
Creates a new storage bucket.
- `--name`: Bucket name (required).
- `--public`: Make bucket public (flag).

### `list-files`
Lists files in a bucket.
- `--bucket`: Bucket name (required).
- `--prefix`: Path prefix to filter files.
- `--limit`: Max results (default: 100).

### `upload`
Uploads a local file to a bucket.
- `--bucket`: Bucket name (required).
- `--file`: Local file path (required).
- `--path`: Destination path in bucket (required).

### `download`
Downloads a file from a bucket.
- `--bucket`: Bucket name (required).
- `--path`: File path in bucket (required).
- `--output`: Local output path (required).

### `delete-file`
Deletes a file from a bucket.
- `--bucket`: Bucket name (required).
- `--path`: File path in bucket (required).

## Dependencies
- `SUPABASE_URL` environment variable (Supabase project URL).
- `SUPABASE_SERVICE_KEY` environment variable (service role key).
- Python `requests` library (`pip install requests`).
