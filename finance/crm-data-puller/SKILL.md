---
name: crm-data-puller
id: OC-0162
version: 1.0.0
description: "CRM Data Puller - Fetch deals and contact data from HubSpot or Salesforce"
env:
  - HUBSPOT_TOKEN
commands:
  - contacts
  - deals
  - pipeline
  - search-contact
  - create-contact
---

# CRM Data Puller

Fetch, search, and manage CRM data from HubSpot directly from the terminal. View contacts, deals, and pipeline status.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `HUBSPOT_TOKEN` — HubSpot private app access token

## Commands

| Command | Description |
|---------|-------------|
| `contacts` | List recent contacts |
| `deals` | List deals by stage or owner |
| `pipeline` | Show deal pipeline summary |
| `search-contact` | Search contacts by name or email |
| `create-contact` | Create a new contact |

## Usage

```bash
export HUBSPOT_TOKEN="your_token"

# List recent contacts
python3 scripts/crm_data_puller.py contacts --limit 20

# List open deals
python3 scripts/crm_data_puller.py deals --stage "presentationscheduled"

# View pipeline summary
python3 scripts/crm_data_puller.py pipeline

# Search for a contact
python3 scripts/crm_data_puller.py search-contact --query "john@acme.com"

# Create a new contact
python3 scripts/crm_data_puller.py create-contact --email "new@client.com" --name "Jane Doe" --company "Acme"
```
