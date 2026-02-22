---
name: invoice-generator
id: OC-0161
version: 1.0.0
description: "Invoice Generator - Create and send PDF invoices from structured data"
env:
  - RESEND_API_KEY
commands:
  - create
  - list
  - send
  - mark-paid
---

# Invoice Generator

Generate professional invoices as text/HTML, track them, and optionally send via email.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `RESEND_API_KEY` — optional, for email delivery via Resend

## Commands

| Command | Description |
|---------|-------------|
| `create` | Create a new invoice |
| `list` | List all invoices |
| `send` | Email an invoice to a client |
| `mark-paid` | Mark an invoice as paid |

## Usage

```bash
# Create an invoice
python3 scripts/invoice_generator.py create \
  --client "Acme Corp" \
  --client-email "billing@acme.com" \
  --items "Web Development:40h:150,SEO Audit:1:500" \
  --due-days 30

# List all invoices
python3 scripts/invoice_generator.py list

# Send invoice by email
python3 scripts/invoice_generator.py send --invoice-id INV-001

# Mark as paid
python3 scripts/invoice_generator.py mark-paid --invoice-id INV-001
```
