---
name: netlify-controller
id: OC-0010
version: 1.0.0
description: "Netlify Site Controller - Manage redirects, forms, split testing"
env:
  - NETLIFY_TOKEN
commands:
  - list-sites
  - deploy
  - get-site
  - list-forms
  - list-submissions
---

# Netlify Site Controller

Control Netlify sites, deployments, forms, and form submissions.

## Prerequisites

- A valid `NETLIFY_TOKEN` environment variable.

## Commands

| Command            | Description                        |
|--------------------|------------------------------------|
| `list-sites`       | List all Netlify sites             |
| `deploy`           | Trigger a new site deploy          |
| `get-site`         | Get details of a specific site     |
| `list-forms`       | List forms for a site              |
| `list-submissions` | List form submissions              |

## Usage

```bash
export NETLIFY_TOKEN="your-token"
python3 scripts/netlify_controller.py list-sites
python3 scripts/netlify_controller.py deploy --site-id abc123
python3 scripts/netlify_controller.py list-forms --site-id abc123
```
