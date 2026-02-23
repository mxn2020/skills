---
name: financial-report-summarizer
id: OC-0164
version: 1.0.0
description: "Financial Report Summarizer - Parse 10-K/10-Q filings and extract key metrics"
env:
  - OPENAI_API_KEY
  - SEC_API_KEY
commands:
  - search-filings
  - summarize
  - key-metrics
  - compare
---

# Financial Report Summarizer

Search SEC EDGAR filings, fetch financial reports, and extract key metrics using AI analysis.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `OPENAI_API_KEY` — for AI-powered summarization
- `SEC_API_KEY` — optional, from sec-api.io for enhanced search

## Commands

| Command | Description |
|---------|-------------|
| `search-filings` | Search SEC EDGAR for company filings |
| `summarize` | AI-summarize a 10-K or 10-Q filing |
| `key-metrics` | Extract key financial metrics from a filing |
| `compare` | Compare two quarters/years |

## Usage

```bash
export OPENAI_API_KEY="your_key"

# Search for Apple's 10-K filings
python3 scripts/financial_report_summarizer.py search-filings --company "Apple" --form "10-K"

# Summarize a filing by CIK and accession number
python3 scripts/financial_report_summarizer.py summarize --cik "0000320193" --form "10-K"

# Extract key metrics
python3 scripts/financial_report_summarizer.py key-metrics --cik "0000320193"
```
