---
name: twilio-sms
id: OC-0076
version: 1.0.0
description: "Twilio SMS & WhatsApp – Send and receive SMS/WhatsApp messages programmatically"
env:
  - TWILIO_ACCOUNT_SID
  - TWILIO_AUTH_TOKEN
  - TWILIO_PHONE_NUMBER
commands:
  - send-sms
  - send-whatsapp
  - list-messages
  - get-message
  - list-phone-numbers
---

# Twilio SMS & WhatsApp

Send and receive SMS and WhatsApp messages programmatically via the Twilio API.

## Prerequisites

- `TWILIO_ACCOUNT_SID` – Twilio Account SID.
- `TWILIO_AUTH_TOKEN` – Twilio Auth Token.
- `TWILIO_PHONE_NUMBER` – Default Twilio phone number (E.164 format, e.g. +15551234567).

## Commands

| Command              | Description                              |
|----------------------|------------------------------------------|
| `send-sms`           | Send an SMS message                      |
| `send-whatsapp`      | Send a WhatsApp message                  |
| `list-messages`      | List recent messages                     |
| `get-message`        | Get details for a specific message       |
| `list-phone-numbers` | List phone numbers on the account        |

## Usage

```bash
export TWILIO_ACCOUNT_SID="your-account-sid"
export TWILIO_AUTH_TOKEN="your-auth-token"
export TWILIO_PHONE_NUMBER="+15551234567"
python3 scripts/twilio_sms.py send-sms --to "+15559876543" --body "Hello from Twilio!"
python3 scripts/twilio_sms.py send-whatsapp --to "+15559876543" --body "Hello from WhatsApp!"
python3 scripts/twilio_sms.py list-messages --limit 10
python3 scripts/twilio_sms.py get-message --message-sid SM1234567890abcdef1234567890abcdef
python3 scripts/twilio_sms.py list-phone-numbers
```
