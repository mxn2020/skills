---
name: pika-animator
id: OC-0095
version: 1.0.0
description: "Pika Labs video animation – animate images and generate videos from text"
env:
  - PIKA_API_KEY
commands:
  - animate
  - text-to-video
  - get-video
  - list-videos
---

# Pika Animator

Animate images and generate videos from text using Pika Labs' AI video platform.

## Prerequisites
- A valid `PIKA_API_KEY` environment variable.

## Commands
| Command          | Description                                |
|------------------|--------------------------------------------|
| `animate`        | Animate a static image                     |
| `text-to-video`  | Generate a video from a text prompt        |
| `get-video`      | Get status and download URL of a video     |
| `list-videos`    | List recent video generations              |

## Usage
```bash
export PIKA_API_KEY="your_key"
python3 scripts/pika_animator.py animate --input photo.jpg --prompt "Gentle breeze" --motion-strength 3 --output-dir ./videos
python3 scripts/pika_animator.py text-to-video --prompt "A rocket launching into space" --duration 5 --ratio 16:9 --output-dir ./videos
python3 scripts/pika_animator.py get-video --video-id "vid_abc123"
python3 scripts/pika_animator.py list-videos --limit 10
```
