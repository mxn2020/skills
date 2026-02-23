---
name: adobe-firefly
id: OC-0088
version: 1.0.0
description: "Adobe Firefly image generation – generate, expand, and edit images via Adobe's API"
env:
  - FIREFLY_CLIENT_ID
  - FIREFLY_CLIENT_SECRET
commands:
  - generate
  - expand
  - remove-background
  - generative-fill
  - list-styles
---

# Adobe Firefly

Generate and manipulate images using Adobe Firefly's commercial-safe generative AI.

## Prerequisites
- A valid `FIREFLY_CLIENT_ID` environment variable.
- A valid `FIREFLY_CLIENT_SECRET` environment variable.

## Commands
| Command               | Description                                    |
|-----------------------|------------------------------------------------|
| `generate`            | Generate images from a text prompt             |
| `expand`              | Expand image canvas with AI-generated content  |
| `remove-background`   | Remove the background from an image            |
| `generative-fill`     | Fill a masked area with generated content      |
| `list-styles`         | List available content styles                  |

## Usage
```bash
export FIREFLY_CLIENT_ID="your_client_id"
export FIREFLY_CLIENT_SECRET="your_client_secret"
python3 scripts/adobe_firefly.py generate --prompt "A serene Japanese garden" --output-dir ./output
python3 scripts/adobe_firefly.py expand --input photo.png --right 512 --prompt "More garden" --output expanded.png
python3 scripts/adobe_firefly.py remove-background --input portrait.png --output nobg.png
python3 scripts/adobe_firefly.py generative-fill --input photo.png --mask mask.png --prompt "A stone fountain" --output filled.png
python3 scripts/adobe_firefly.py list-styles
```
