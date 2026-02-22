---
name: cloudinary-manager
id: OC-0065
version: 1.0.0
description: "Cloudinary Asset Manager - Upload, transform, and optimize images"
env:
  - CLOUDINARY_URL
  - CLOUDINARY_CLOUD_NAME
  - CLOUDINARY_API_KEY
  - CLOUDINARY_API_SECRET
commands:
  - upload
  - list
  - get
  - transform
  - delete
  - search
---

# Cloudinary Asset Manager

Upload, transform, and optimize images with Cloudinary.

## Prerequisites

- `CLOUDINARY_URL` – Full Cloudinary URL (e.g. `cloudinary://key:secret@cloud`), **or** set all three:
  - `CLOUDINARY_CLOUD_NAME` – Cloud name.
  - `CLOUDINARY_API_KEY` – API key.
  - `CLOUDINARY_API_SECRET` – API secret.

## Commands

| Command     | Description                                |
|-------------|--------------------------------------------|
| `upload`    | Upload an image from a URL or local path   |
| `list`      | List resources in your account             |
| `get`       | Get details for a specific asset           |
| `transform` | Generate a transformation URL              |
| `delete`    | Delete a resource by public ID             |
| `search`    | Search assets with an expression           |

## Usage

```bash
export CLOUDINARY_URL="cloudinary://key:secret@cloud"
python3 scripts/cloudinary_manager.py upload --url "https://example.com/photo.jpg" --public-id "my-photo"
python3 scripts/cloudinary_manager.py list --max-results 10
python3 scripts/cloudinary_manager.py get --public-id "my-photo"
python3 scripts/cloudinary_manager.py transform --public-id "my-photo" --width 400 --height 300 --crop fill
python3 scripts/cloudinary_manager.py delete --public-id "my-photo"
python3 scripts/cloudinary_manager.py search --expression "cat AND format:jpg" --max-results 5
```
