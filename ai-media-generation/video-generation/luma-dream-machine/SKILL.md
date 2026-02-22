---
name: luma-dream-machine
id: OC-0096
version: 1.0.0
description: "Luma AI Dream Machine – generate and extend videos from text or images"
env:
  - LUMAAI_API_KEY
commands:
  - generate
  - image-to-video
  - extend
  - get-generation
  - list-generations
---

# Luma Dream Machine

Generate high-quality, realistic videos using Luma AI's Dream Machine model.

## Prerequisites
- A valid `LUMAAI_API_KEY` environment variable.

## Commands
| Command            | Description                              |
|--------------------|------------------------------------------|
| `generate`         | Generate a video from a text prompt      |
| `image-to-video`   | Create a video starting from an image    |
| `extend`           | Extend an existing video generation      |
| `get-generation`   | Get status/result of a generation        |
| `list-generations` | List recent video generations            |

## Usage
```bash
export LUMAAI_API_KEY="your_key"
python3 scripts/luma_dream_machine.py generate --prompt "Waves crashing on a rocky shore" --aspect-ratio 16:9 --output-dir ./videos
python3 scripts/luma_dream_machine.py image-to-video --input photo.jpg --prompt "The scene slowly pans right" --output-dir ./videos
python3 scripts/luma_dream_machine.py extend --generation-id "gen_abc123" --prompt "Continue zooming out" --output-dir ./videos
python3 scripts/luma_dream_machine.py get-generation --generation-id "gen_abc123"
python3 scripts/luma_dream_machine.py list-generations --limit 5
```
