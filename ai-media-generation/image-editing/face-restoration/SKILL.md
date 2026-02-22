---
name: face-restoration
id: OC-0093
version: 1.0.0
description: "Restore and enhance faces in photos using GFPGAN via Replicate"
env:
  - REPLICATE_API_TOKEN
commands:
  - restore
  - enhance
---

# Face Restoration

Restore and enhance degraded faces using GFPGAN running on Replicate.

## Prerequisites
- A valid `REPLICATE_API_TOKEN` environment variable.

## Commands
| Command    | Description                                        |
|------------|----------------------------------------------------|
| `restore`  | Restore faces in an image using GFPGAN             |
| `enhance`  | Restore faces with optional background upsampling  |

## Usage
```bash
export REPLICATE_API_TOKEN="r8_..."
python3 scripts/face_restoration.py restore --input old_photo.jpg --scale 2 --output restored.png
python3 scripts/face_restoration.py enhance --input portrait.jpg --scale 4 --bg-upsampler --output enhanced.png
```
