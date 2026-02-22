---
name: ideogram-typographer
id: OC-0087
version: 1.0.0
description: "Ideogram AI image generation – excels at rendering readable text within images"
env:
  - IDEOGRAM_API_KEY
commands:
  - generate
  - remix
  - describe
  - list-styles
---

# Ideogram Typographer

Generate images with accurate text rendering using Ideogram AI's V2 model.

## Prerequisites
- A valid `IDEOGRAM_API_KEY` environment variable.

## Commands
| Command        | Description                                    |
|----------------|------------------------------------------------|
| `generate`     | Generate an image from a prompt                |
| `remix`        | Remix an existing image with a new prompt      |
| `describe`     | Get a text description of an image             |
| `list-styles`  | List available style types                     |

## Usage
```bash
export IDEOGRAM_API_KEY="your_key"
python3 scripts/ideogram_typographer.py generate --prompt "A coffee shop menu with bold text" --style-type DESIGN --output menu.png
python3 scripts/ideogram_typographer.py remix --input original.png --prompt "Same but in dark mode" --strength 0.6 --output remixed.png
python3 scripts/ideogram_typographer.py describe --input photo.png
python3 scripts/ideogram_typographer.py list-styles
```
