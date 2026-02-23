---
name: azure-resources
id: OC-0021
version: 1.0.0
description: "Azure Resource Manager - List and audit resource groups"
env:
  - AZURE_SUBSCRIPTION_ID
commands:
  - list-groups
  - list-resources
  - get-resource
  - list-tags
  - audit
---

# Azure Resource Manager

List, inspect, and audit Azure resource groups and resources.

## Prerequisites

- `az` CLI authenticated and `AZURE_SUBSCRIPTION_ID` set.

## Commands

| Command          | Description                          |
|------------------|--------------------------------------|
| `list-groups`    | List all resource groups             |
| `list-resources` | List resources in a group            |
| `get-resource`   | Get details of a specific resource   |
| `list-tags`      | List tags for a resource group       |
| `audit`          | Audit untagged resources             |

## Usage

```bash
export AZURE_SUBSCRIPTION_ID="your-sub-id"
python3 scripts/azure_resources.py list-groups
python3 scripts/azure_resources.py list-resources --group my-rg
python3 scripts/azure_resources.py audit --group my-rg
```
