---
name: midjourney-prompter
id: OC-0083
version: 1.0.0
description: "Midjourney image generation – create and manage AI-generated artwork via useapi.net"
env:
  - MIDJOURNEY_API_KEY
commands:
  - imagine
  - upscale
  - variations
  - status
  - list-jobs
---

# Midjourney Prompter

Generate stunning AI artwork using Midjourney via the useapi.net unofficial API.

## Prerequisites
- A valid `MIDJOURNEY_API_KEY` environment variable (from useapi.net).

## Commands
| Command       | Description                                      |
|---------------|--------------------------------------------------|
| `imagine`     | Generate an image from a prompt                  |
| `upscale`     | Upscale a specific image from a job              |
| `variations`  | Create variations of a job image                 |
| `status`      | Get status of a job                              |
| `list-jobs`   | List recent generation jobs                      |

## Usage
```bash
export MIDJOURNEY_API_KEY="your_key"
python3 scripts/midjourney_prompter.py imagine --prompt "A serene mountain lake, photorealistic" --ar 16:9 --output mountain.png
python3 scripts/midjourney_prompter.py upscale --job-id "abc123" --index 1
python3 scripts/midjourney_prompter.py variations --job-id "abc123" --index 2
python3 scripts/midjourney_prompter.py status --job-id "abc123"
python3 scripts/midjourney_prompter.py list-jobs --limit 5
```
