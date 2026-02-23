---
name: context-compressor
id: OC-0117
version: 1.0.0
description: "Context Compressor - Summarize or truncate conversation history to fit context windows"
env:
  - OPENAI_API_KEY
commands:
  - compress
  - summarize-history
  - truncate
  - estimate-tokens
---

# Context Compressor

Reduce conversation history and long documents to fit within LLM context windows using summarization or smart truncation.

## Prerequisites

- `OPENAI_API_KEY`
- Optional: `pip install tiktoken`

## Commands

| Command | Description |
|---------|-------------|
| `compress` | Compress a file to a target token count |
| `summarize-history` | Summarize a conversation history JSON file |
| `truncate` | Truncate text to a max token count |
| `estimate-tokens` | Estimate token count for a file |

## Usage

```bash
export OPENAI_API_KEY="sk-..."

python3 scripts/context_compressor.py compress --file long_doc.txt --target-tokens 2000
python3 scripts/context_compressor.py summarize-history --file conversation.json
python3 scripts/context_compressor.py truncate --file doc.txt --max-tokens 4000 --strategy tail
python3 scripts/context_compressor.py estimate-tokens --file doc.txt
```
