---
name: leonardo-ai
id: OC-0086
version: 1.0.0
description: "Leonardo.ai image generation – create images with fine-tuned models"
env:
  - LEONARDO_API_KEY
commands:
  - generate
  - get-generation
  - list-models
  - list-generations
---

# Leonardo.ai

Generate images using Leonardo.ai's fine-tuned models with full parameter control.

## Prerequisites
- A valid `LEONARDO_API_KEY` environment variable.

## Commands
| Command            | Description                            |
|--------------------|----------------------------------------|
| `generate`         | Generate images from a prompt          |
| `get-generation`   | Get details of a generation by ID      |
| `list-models`      | List available Leonardo models         |
| `list-generations` | List recent generations                |

## Usage
```bash
export LEONARDO_API_KEY="your_key"
python3 scripts/leonardo_ai.py generate --prompt "Portrait of an astronaut" --num-images 2 --output-dir ./output
python3 scripts/leonardo_ai.py get-generation --generation-id "gen_abc123"
python3 scripts/leonardo_ai.py list-models
python3 scripts/leonardo_ai.py list-generations --limit 5
```
