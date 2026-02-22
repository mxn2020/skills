---
name: inpainting-agent
id: OC-0091
version: 1.0.0
description: "AI image inpainting – fill, erase, and search-replace image regions via Stability AI"
env:
  - STABILITY_API_KEY
commands:
  - inpaint
  - erase
  - search-and-replace
---

# Inpainting Agent

Fill, erase, or replace regions in images using Stability AI's inpainting API.

## Prerequisites
- A valid `STABILITY_API_KEY` environment variable.

## Commands
| Command               | Description                                        |
|-----------------------|----------------------------------------------------|
| `inpaint`             | Fill a masked region using a text prompt           |
| `erase`               | Erase a masked region from an image                |
| `search-and-replace`  | Find and replace an object described in a prompt   |

## Usage
```bash
export STABILITY_API_KEY="sk-..."
python3 scripts/inpainting_agent.py inpaint --input scene.png --mask mask.png --prompt "A red sports car" --output result.png
python3 scripts/inpainting_agent.py erase --input photo.png --mask watermark_mask.png --output clean.png
python3 scripts/inpainting_agent.py search-and-replace --input photo.png --search-prompt "blue car" --prompt "red Ferrari" --output swapped.png
```
