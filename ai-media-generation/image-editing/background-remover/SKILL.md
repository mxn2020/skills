---
name: background-remover
id: OC-0089
version: 1.0.0
description: "Remove image backgrounds instantly using the remove.bg API"
env:
  - REMOVEBG_API_KEY
commands:
  - remove
  - bulk-remove
---

# Background Remover

Remove backgrounds from images with high accuracy using the remove.bg API.

## Prerequisites
- A valid `REMOVEBG_API_KEY` environment variable.

## Commands
| Command        | Description                                    |
|----------------|------------------------------------------------|
| `remove`       | Remove background from a single image          |
| `bulk-remove`  | Remove backgrounds from all images in a folder |

## Usage
```bash
export REMOVEBG_API_KEY="your_key"
python3 scripts/background_remover.py remove --input photo.jpg --output nobg.png --size hd --type person
python3 scripts/background_remover.py bulk-remove --input-dir ./photos --output-dir ./nobg --size regular
```
