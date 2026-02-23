---
name: legal-doc-scanner
id: OC-0171
version: 1.0.0
description: "Legal Document Scanner - Summarize TOS changes, lease agreements, and contracts"
env:
  - OPENAI_API_KEY
commands:
  - summarize
  - flag-risks
  - compare
  - extract-clauses
---

# Legal Document Scanner

Analyze legal documents, terms of service, contracts, and lease agreements using AI. Extract key clauses, flag potential risks, and generate plain-English summaries.

**⚠ Disclaimer: Not legal advice. Always consult a qualified attorney for important legal matters.**

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `OPENAI_API_KEY` — for AI analysis

## Commands

| Command | Description |
|---------|-------------|
| `summarize` | Plain-English summary of a document |
| `flag-risks` | Identify potentially problematic clauses |
| `compare` | Compare two documents for differences |
| `extract-clauses` | Extract specific clause types |

## Usage

```bash
export OPENAI_API_KEY="your_key"

# Summarize a document
python3 scripts/legal_doc_scanner.py summarize --file contract.txt

# Flag risky clauses
python3 scripts/legal_doc_scanner.py flag-risks --file tos.txt

# Compare two versions
python3 scripts/legal_doc_scanner.py compare --file-a tos_v1.txt --file-b tos_v2.txt

# Extract termination clauses
python3 scripts/legal_doc_scanner.py extract-clauses --file lease.txt --clause-type termination
```
