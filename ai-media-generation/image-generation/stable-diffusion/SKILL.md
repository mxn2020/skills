---
name: stable-diffusion
id: OC-0084
version: 1.0.0
description: "Stability AI SDXL image generation – generate, upscale, and inpaint images"
env:
  - STABILITY_API_KEY
commands:
  - generate
  - upscale
  - inpaint
  - list-engines
---

# Stable Diffusion (SDXL)

Generate, upscale, and inpaint images using Stability AI's SDXL models.

## Prerequisites
- A valid `STABILITY_API_KEY` environment variable.

## Commands
| Command         | Description                                |
|-----------------|--------------------------------------------|
| `generate`      | Generate an image from a text prompt       |
| `upscale`       | Upscale an existing image                  |
| `inpaint`       | Fill a masked region with generated content|
| `list-engines`  | List available Stability AI engines        |

## Usage
```bash
export STABILITY_API_KEY="sk-..."
python3 scripts/stable_diffusion.py generate --prompt "A wolf howling at the moon" --width 1024 --height 1024 --output wolf.png
python3 scripts/stable_diffusion.py upscale --input image.png --width 2048 --output upscaled.png
python3 scripts/stable_diffusion.py inpaint --init-image base.png --mask-image mask.png --prompt "A garden" --output result.png
python3 scripts/stable_diffusion.py list-engines
```
