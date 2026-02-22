---
name: model-benchmarker
id: OC-0119
version: 1.0.0
description: "Model Benchmarker - Run the same prompt against multiple LLMs and compare output"
env:
  - OPENAI_API_KEY
  - ANTHROPIC_API_KEY
commands:
  - run-benchmark
  - compare
  - list-models
  - export-results
---

# Model Benchmarker

Benchmark prompts across OpenAI, Anthropic, and other models to compare quality, speed, and cost.

## Prerequisites

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY` (optional)

## Commands

| Command | Description |
|---------|-------------|
| `run-benchmark` | Run a prompt against multiple models |
| `compare` | Compare results from a benchmark run |
| `list-models` | List available models with pricing |
| `export-results` | Export benchmark results |

## Usage

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

python3 scripts/model_benchmarker.py run-benchmark --prompt "Explain quantum entanglement in 3 sentences" --runs 2
python3 scripts/model_benchmarker.py compare --results-file results.json
python3 scripts/model_benchmarker.py list-models
python3 scripts/model_benchmarker.py export-results --results-file results.json --format md
```
