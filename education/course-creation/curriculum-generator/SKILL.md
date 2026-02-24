---
name: curriculum-generator
id: OC-0189
version: 1.0.0
description: "Break down a complex topic into structured modules, lessons, and quizzes."
env:
  - OPENAI_API_KEY
commands:
  - generate-outline
  - generate-lesson
---

# Curriculum Generator

Break down a complex topic into structured modules, lessons, and quizzes.

## Prerequisites
- A valid `OPENAI_API_KEY` environment variable.

## Commands
| Command            | Description                              |
|--------------------|------------------------------------------|
| `generate-outline` | Generate a full course outline from a topic overview |
| `generate-lesson`  | Generate content for a specific lesson and associated quiz |

## Usage
```bash
export OPENAI_API_KEY="sk-..."
python3 scripts/curriculum_generator.py generate-outline --topic "Introduction to Quantum Computing"
python3 scripts/curriculum_generator.py generate-lesson --module "1.1" --topic "Quantum Superposition"
```
