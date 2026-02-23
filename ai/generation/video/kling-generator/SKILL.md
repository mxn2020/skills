---
name: kling-generator
id: OC-0097
version: 1.0.0
description: "Kling AI video generation – create videos from text or images with KLING models"
env:
  - KLING_ACCESS_KEY
  - KLING_SECRET_KEY
commands:
  - text-to-video
  - image-to-video
  - get-task
  - list-tasks
---

# Kling Generator

Generate high-quality videos from text or images using Kling AI's video models.

## Prerequisites
- A valid `KLING_ACCESS_KEY` environment variable.
- A valid `KLING_SECRET_KEY` environment variable.

## Commands
| Command           | Description                              |
|-------------------|------------------------------------------|
| `text-to-video`   | Generate a video from a text prompt      |
| `image-to-video`  | Animate an image into a video            |
| `get-task`        | Get status and result of a task          |
| `list-tasks`      | List recent video generation tasks       |

## Usage
```bash
export KLING_ACCESS_KEY="your_access_key"
export KLING_SECRET_KEY="your_secret_key"
python3 scripts/kling_generator.py text-to-video --prompt "A bird flying over mountains" --duration 5 --mode pro --output-dir ./videos
python3 scripts/kling_generator.py image-to-video --input scene.jpg --prompt "The clouds begin to move" --output-dir ./videos
python3 scripts/kling_generator.py get-task --task-id "task_abc123"
python3 scripts/kling_generator.py list-tasks --limit 10
```
