---
name: runway-gen3
id: OC-0094
version: 1.0.0
description: "Runway Gen-3 Alpha video generation – create videos from text or images"
env:
  - RUNWAYML_API_SECRET
commands:
  - generate
  - image-to-video
  - get-task
  - list-tasks
---

# Runway Gen-3

Generate cinematic videos from text prompts or images using Runway Gen-3 Alpha.

## Prerequisites
- A valid `RUNWAYML_API_SECRET` environment variable.

## Commands
| Command          | Description                              |
|------------------|------------------------------------------|
| `generate`       | Generate a video from a text prompt      |
| `image-to-video` | Animate an image with a text prompt      |
| `get-task`       | Get status and result of a video task    |
| `list-tasks`     | List recent generation tasks             |

## Usage
```bash
export RUNWAYML_API_SECRET="your_secret"
python3 scripts/runway_gen3.py generate --prompt "A drone shot flying over a forest" --duration 10 --output-dir ./videos
python3 scripts/runway_gen3.py image-to-video --input photo.jpg --prompt "The scene comes to life" --output-dir ./videos
python3 scripts/runway_gen3.py get-task --task-id "task_abc123"
python3 scripts/runway_gen3.py list-tasks --limit 5
```
