---
name: nix-flake-generator
id: OC-0194
version: 1.0.0
description: "Create reproducible development environments and configurations automatically."
env:
  - OPENAI_API_KEY
commands:
  - generate-flake
  - validate
---

# Nix Flake Generator

Create reproducible development environments and configurations automatically.

## Prerequisites
- A valid `OPENAI_API_KEY` environment variable.

## Commands
| Command          | Description                              |
|------------------|------------------------------------------|
| `generate-flake` | Generate `flake.nix` based on environment requirements |
| `validate`       | Validate the syntax of the generated flake file |

## Usage
```bash
export OPENAI_API_KEY="sk-..."
python3 scripts/nix_flake_generator.py generate-flake --prompt "A Python environment with numpy, scipy, and jupyterlab"
python3 scripts/nix_flake_generator.py validate --dir .
```
