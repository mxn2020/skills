---
name: dalle3-artist
id: OC-0082
version: 1.0.0
description: "DALL-E 3 image generation – generate high-quality images from text prompts"
env:
  - OPENAI_API_KEY
commands:
  - generate
  - variations
  - list-models
---

# DALL-E 3 Artist

Generate high-quality images from text prompts using OpenAI's DALL-E 3 model.

## Prerequisites
- A valid `OPENAI_API_KEY` environment variable.

## Commands
| Command        | Description                              |
|----------------|------------------------------------------|
| `generate`     | Generate an image from a text prompt     |
| `variations`   | Create variations of an existing image   |
| `list-models`  | List available DALL-E models             |

## Usage
```bash
export OPENAI_API_KEY="sk-..."
python3 scripts/dalle3_artist.py generate --prompt "A futuristic city at sunset" --size 1024x1024 --quality hd --output city.png
python3 scripts/dalle3_artist.py variations --input image.png --n 2 --output variation.png
python3 scripts/dalle3_artist.py list-models
```
