---
name: resend-email
id: OC-0075
version: 1.0.0
description: "Resend Email Sender – Send transactional emails with templates"
env:
  - RESEND_API_KEY
commands:
  - send
  - list-emails
  - get-email
  - list-domains
  - list-api-keys
---

# Resend Email Sender

Send transactional emails, manage domains, and inspect API keys via the Resend API.

## Prerequisites
- A valid `RESEND_API_KEY` environment variable.

## Commands
| Command         | Description                     |
|-----------------|---------------------------------|
| `send`          | Send a transactional email      |
| `list-emails`   | List recently sent emails       |
| `get-email`     | Get details of a specific email |
| `list-domains`  | List verified sending domains   |
| `list-api-keys` | List API keys for the account   |

## Usage
```bash
export RESEND_API_KEY="re_your_api_key"
python3 scripts/resend_email.py send --from "you@example.com" --to "user@example.com" --subject "Hello" --html "<h1>Hi</h1>"
python3 scripts/resend_email.py list-emails
python3 scripts/resend_email.py get-email --email-id "email_123"
python3 scripts/resend_email.py list-domains
python3 scripts/resend_email.py list-api-keys
```
