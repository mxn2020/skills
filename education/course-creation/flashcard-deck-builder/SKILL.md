---
name: flashcard-deck-builder
id: OC-0190
version: 1.0.0
description: "Extract key concepts from documents and prepare an Anki-compatible CSV for spaced repetition."
env:
  - OPENAI_API_KEY
commands:
  - extract-concepts
  - build-deck
---

# Flashcard Deck Builder

Extract key concepts from documents and prepare an Anki-compatible CSV for spaced repetition.

## Prerequisites
- A valid `OPENAI_API_KEY` environment variable.

## Commands
| Command            | Description                              |
|--------------------|------------------------------------------|
| `extract-concepts` | Extract key ideas and terms from a provided source document |
| `build-deck`       | Prepare an Anki-compatible CSV using extracted concepts |

## Usage
```bash
export OPENAI_API_KEY="sk-..."
python3 scripts/flashcard_deck_builder.py extract-concepts --input document.pdf
python3 scripts/flashcard_deck_builder.py build-deck --input concepts.json --output deck.csv
```
