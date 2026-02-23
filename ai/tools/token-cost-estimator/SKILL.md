---
name: token-cost-estimator
id: OC-0116
version: 1.0.0
description: "Token Cost Estimator - Calculate token counts and costs before running prompts"
env: []
commands:
  - estimate
  - estimate-file
  - compare-models
  - show-pricing
---

# Token Cost Estimator

Estimate token counts and API costs for prompts across multiple models before running them.

## Prerequisites

- Optional: `pip install tiktoken` for accurate tokenization
- Falls back to character-based approximation if tiktoken unavailable

## Commands

| Command | Description |
|---------|-------------|
| `estimate` | Estimate tokens and cost for inline text |
| `estimate-file` | Estimate tokens and cost for a file |
| `compare-models` | Compare cost across top models |
| `show-pricing` | Show current per-token pricing table |

## Usage

```bash
python3 scripts/token_cost_estimator.py estimate --text "Your prompt here" --model gpt-4o
python3 scripts/token_cost_estimator.py estimate-file --file prompt.txt --model claude-3-5-sonnet
python3 scripts/token_cost_estimator.py compare-models --text "Your prompt here"
python3 scripts/token_cost_estimator.py show-pricing
```
