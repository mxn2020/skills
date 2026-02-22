---
name: gcloud-storage
id: OC-0017
version: 1.0.0
description: "Google Cloud Storage Manager - Manage buckets and lifecycle"
env:
  - GOOGLE_CLOUD_PROJECT
commands:
  - list-buckets
  - list-objects
  - upload
  - download
  - set-lifecycle
---

# Google Cloud Storage Manager

Manage GCS buckets, objects, and lifecycle policies.

## Prerequisites

- `gcloud`/`gsutil` CLI authenticated and `GOOGLE_CLOUD_PROJECT` set.

## Commands

| Command         | Description                          |
|-----------------|--------------------------------------|
| `list-buckets`  | List all GCS buckets                 |
| `list-objects`  | List objects in a bucket             |
| `upload`        | Upload a file to GCS                 |
| `download`      | Download an object from GCS          |
| `set-lifecycle` | Set bucket lifecycle rules           |

## Usage

```bash
export GOOGLE_CLOUD_PROJECT="my-project"
python3 scripts/gcloud_storage.py list-buckets
python3 scripts/gcloud_storage.py upload --bucket my-bucket --file ./data.csv --dest data/data.csv
python3 scripts/gcloud_storage.py set-lifecycle --bucket my-bucket --rules lifecycle.json
```
