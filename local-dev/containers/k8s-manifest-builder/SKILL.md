---
name: k8s-manifest-builder
id: OC-0193
version: 1.0.0
description: "Generate and validate Kubernetes deployments, services, and ingress configurations."
env:
  - OPENAI_API_KEY
commands:
  - generate
  - apply-dry-run
---

# K8s Manifest Builder

Generate and validate Kubernetes deployments, services, and ingress configurations.

## Prerequisites
- A valid `OPENAI_API_KEY` environment variable.

## Commands
| Command         | Description                              |
|-----------------|------------------------------------------|
| `generate`      | Generate Kubernetes manifests from a detailed description |
| `apply-dry-run` | Perform a dry-run apply to check manifest validity       |

## Usage
```bash
export OPENAI_API_KEY="sk-..."
python3 scripts/k8s_manifest_builder.py generate --prompt "A frontend deployment with three replicas load-balanced via Ingress, speaking to a stateful database."
python3 scripts/k8s_manifest_builder.py apply-dry-run --dir ./manifests
```
