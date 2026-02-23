---
name: flux-generator
id: OC-0085
version: 1.0.0
description: "FLUX image generation – fast high-quality images via Replicate (Schnell/Dev)"
env:
  - REPLICATE_API_TOKEN
commands:
  - generate
  - list-models
---

# FLUX Generator

Generate high-quality images using FLUX Schnell or Dev models via Replicate.

## Prerequisites
- A valid `REPLICATE_API_TOKEN` environment variable.

## Commands
| Command        | Description                          |
|----------------|--------------------------------------|
| `generate`     | Generate an image from a prompt      |
| `list-models`  | List available FLUX models           |

## Usage
```bash
export REPLICATE_API_TOKEN="r8_..."
python3 scripts/flux_generator.py generate --prompt "Neon cyberpunk street at night" --model schnell --output image.png
python3 scripts/flux_generator.py generate --prompt "Oil painting of a lighthouse" --model dev --steps 25 --output painting.png
python3 scripts/flux_generator.py list-models
```
