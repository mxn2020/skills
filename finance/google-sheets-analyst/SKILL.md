---
name: google-sheets-analyst
id: OC-0163
version: 1.0.0
description: "Google Sheets Analyst - Read, write, and analyze data in spreadsheets"
env:
  - GOOGLE_SHEETS_TOKEN
commands:
  - read
  - write
  - append
  - stats
  - list-sheets
---

# Google Sheets Analyst

Read, write, and analyze data in Google Spreadsheets directly from the terminal via the Sheets API.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `GOOGLE_SHEETS_TOKEN` — OAuth 2.0 bearer token with `spreadsheets` scope

## Commands

| Command | Description |
|---------|-------------|
| `read` | Read data from a sheet range |
| `write` | Write data to a sheet range |
| `append` | Append rows to a sheet |
| `stats` | Calculate basic stats on a column |
| `list-sheets` | List sheets in a spreadsheet |

## Usage

```bash
export GOOGLE_SHEETS_TOKEN="your_oauth_token"

# Read a range
python3 scripts/google_sheets_analyst.py read --spreadsheet-id "ID" --range "Sheet1!A1:E10"

# Write data
python3 scripts/google_sheets_analyst.py write --spreadsheet-id "ID" --range "Sheet1!A1" --values "Name,Age,City"

# Append a row
python3 scripts/google_sheets_analyst.py append --spreadsheet-id "ID" --sheet "Sheet1" --values "John,30,NY"

# Get stats for a column
python3 scripts/google_sheets_analyst.py stats --spreadsheet-id "ID" --range "Sheet1!B2:B100"

# List sheets
python3 scripts/google_sheets_analyst.py list-sheets --spreadsheet-id "ID"
```
