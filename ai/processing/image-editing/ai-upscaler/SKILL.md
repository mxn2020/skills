---
name: ai-upscaler
id: OC-0090
version: 1.0.0
description: "AI image upscaling using Real-ESRGAN via Replicate – enhance resolution up to 8x"
env:
  - REPLICATE_API_TOKEN
commands:
  - upscale
  - batch-upscale
---

# AI Upscaler

Upscale images up to 8x using Real-ESRGAN via Replicate with optional face enhancement.

## Prerequisites
- A valid `REPLICATE_API_TOKEN` environment variable.

## Commands
| Command          | Description                                |
|------------------|--------------------------------------------|
| `upscale`        | Upscale a single image                     |
| `batch-upscale`  | Upscale all images in a directory          |

## Usage
```bash
export REPLICATE_API_TOKEN="r8_..."
python3 scripts/ai_upscaler.py upscale --input photo.jpg --scale 4 --output upscaled.png
python3 scripts/ai_upscaler.py upscale --input portrait.jpg --scale 2 --face-enhance --output enhanced.png
python3 scripts/ai_upscaler.py batch-upscale --input-dir ./originals --output-dir ./upscaled --scale 4
```
