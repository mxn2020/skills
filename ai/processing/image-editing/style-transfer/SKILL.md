---
name: style-transfer
id: OC-0092
version: 1.0.0
description: "Apply artistic styles to images using fofr/style-transfer via Replicate"
env:
  - REPLICATE_API_TOKEN
commands:
  - transfer
  - list-styles
---

# Style Transfer

Apply any artistic style to images using Replicate's style-transfer model.

## Prerequisites
- A valid `REPLICATE_API_TOKEN` environment variable.

## Commands
| Command        | Description                              |
|----------------|------------------------------------------|
| `transfer`     | Apply a style image to a content image   |
| `list-styles`  | Show popular style preset descriptions   |

## Usage
```bash
export REPLICATE_API_TOKEN="r8_..."
python3 scripts/style_transfer.py transfer --content photo.jpg --style artwork.jpg --output styled.png
python3 scripts/style_transfer.py transfer --content portrait.jpg --style monet.jpg --style-strength 0.7 --output monet_portrait.png
python3 scripts/style_transfer.py list-styles
```
