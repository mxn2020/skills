---
name: iac-runner
id: OC-0024
version: 1.0.0
description: "Pulumi/Terraform Runner - Execute IaC plans"
env: []
commands:
  - init
  - plan
  - apply
  - destroy
  - list-stacks
---

# Pulumi/Terraform Runner

Run Infrastructure-as-Code operations using Terraform or Pulumi.

## Prerequisites

- `terraform` and/or `pulumi` CLI installed.

## Commands

| Command       | Description                          |
|---------------|--------------------------------------|
| `init`        | Initialize the IaC workspace         |
| `plan`        | Preview changes                      |
| `apply`       | Apply changes                        |
| `destroy`     | Tear down resources                  |
| `list-stacks` | List stacks (Pulumi) or workspaces   |

## Usage

```bash
python3 scripts/iac_runner.py --tool terraform init --dir ./infra
python3 scripts/iac_runner.py --tool terraform plan --dir ./infra
python3 scripts/iac_runner.py --tool pulumi list-stacks
python3 scripts/iac_runner.py --tool terraform apply --dir ./infra --auto-approve
```
