---
name: nvidia-image-gen
version: 1.0.0
description: Generate and edit images using NVIDIA FLUX models. Use when user asks to generate images, create pictures, edit photos, or modify existing images with AI. Supports text-to-image generation and image editing with text prompts.
---

# NVIDIA Image Generation

Generate and edit images using NVIDIA's FLUX models.

## Models

| Model | Use Case | Speed | Quality |
|-------|----------|-------|---------|
| `dev` | High-quality text-to-image | Normal | Best |
| `schnell` | Fast text-to-image | Fast | Good |
| `stable` | Stable Diffusion text-to-image | Fast | Good |
| `kontext` | Image editing | Normal | Best |

## Quick Start

```bash
# Generate an image
python3 skills/nvidia-image-gen/scripts/generate.py "A cute cat in space"

# Edit an existing image
python3 skills/nvidia-image-gen/scripts/generate.py "Add sunglasses" -i photo.jpg -o edited.png
```

## Parameters

### Text-to-Image (dev/schnell)

| Parameter | Short | Default | Description |
|-----------|-------|---------|-------------|
| `prompt` | | (required) | Text description |
| `-o, --output` | | output.png | Output file path |
| `--width` | | 1024 | Output width in pixels |
| `--height` | | 1024 | Output height in pixels |
| `--aspect-ratio` | `-ar` | 1:1 | Aspect ratio preset |
| `--steps` | `-s` | 30 | Diffusion steps |
| `--seed` | | 0 | Random seed (0=random) |
| `--model` | `-m` | auto | Model selection |

### Image Editing (kontext)

| Parameter | Short | Default | Description |
|-----------|-------|---------|-------------|
| `prompt` | | (required) | Edit instruction |
| `-i, --input` | | (required) | Input image path |
| `-o, --output` | | output.png | Output file path |
| `--steps` | `-s` | 30 | Diffusion steps |
| `--cfg` | | 3.5 | Guidance scale |
| `--seed` | | 0 | Random seed |

### Stable Diffusion 3 Medium (stable)

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `prompt` | string | — | ✅ | What you wish to see in the output image (max 10,000 chars) |
| `aspect_ratio` | string | `1:1` | | Aspect ratio. Allowed: `1:1`, `16:9`, `9:16`, `5:4`, `4:5`, `3:2`, `2:3` |
| `cfg_scale` | number | `5` | | Classifier-free guidance scale (max 9). Higher = more aligned, less diverse |
| `negative_prompt` | string | `null` | | What you do *not* want in the image (advanced) |
| `steps` | integer | `50` | | Diffusion steps, 5–100. More steps = higher quality but slower |
| `seed` | integer | `0` | | Random seed (≥ 0). Use `0` for random |
| `output_format` | string | `jpeg` | | Output content-type. Allowed: `jpeg` |
| `mode` | string | `text-to-image` | | Generation mode. Allowed: `text-to-image` |
| `model` | string | `sd3` | | Model to use. Allowed: `sd3` |

## Supported Aspect Ratios

| Ratio | Resolution |
|-------|------------|
| 1:1 | 1024×1024 |
| 16:9 | 1344×768 |
| 9:16 | 768×1344 |
| 4:3 | 1216×832 |
| 3:4 | 832×1216 |

## Examples

### Basic Generation
```bash
python3 skills/nvidia-image-gen/scripts/generate.py "A mountain landscape at sunset"
```

### Wide Format (16:9)
```bash
python3 skills/nvidia-image-gen/scripts/generate.py "A panoramic beach view" -ar 16:9
```

### Portrait Mode (9:16)
```bash
python3 skills/nvidia-image-gen/scripts/generate.py "A professional headshot" -ar 9:16
```

### Custom Size
```bash
python3 skills/nvidia-image-gen/scripts/generate.py "A banner image" --width 1344 --height 768
```

### Fast Generation
```bash
python3 skills/nvidia-image-gen/scripts/generate.py "Quick sketch of a robot" -m schnell
```

### Edit an Image
```bash
python3 skills/nvidia-image-gen/scripts/generate.py "Make the background a sunset" -i input.jpg -o output.png
```

### Reproducible Results
```bash
python3 skills/nvidia-image-gen/scripts/generate.py "A robot" --seed 12345
```

## Output

The script outputs `MEDIA:/path/to/image.png` which can be sent directly to chat.

## API Key

The API key is embedded in the script. To use a different key, set the `NVIDIA_API_KEY` environment variable.
