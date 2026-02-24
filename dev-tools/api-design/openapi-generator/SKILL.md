---
name: openapi-generator
id: OC-0199
version: 1.0.0
description: "Generate comprehensive OpenAPI/Swagger specifications from code or natural language."
env:
  - OPENAI_API_KEY
commands:
  - from-code
  - from-prompt
---

# OpenAPI Generator

Generate comprehensive OpenAPI/Swagger specifications from code or natural language.

## Prerequisites
- A valid `OPENAI_API_KEY` environment variable.

## Commands
| Command       | Description                              |
|---------------|------------------------------------------|
| `from-code`   | Extract API routes and generate OpenAPI from source code |
| `from-prompt` | Scaffold an OpenAPI spec from a natural language design  |

## Usage
```bash
export OPENAI_API_KEY="sk-..."
python3 scripts/openapi_generator.py from-code --source src/routes/ --output swagger.yaml
python3 scripts/openapi_generator.py from-prompt --prompt "A REST API for managing users and roles" --output spec.yaml
```
