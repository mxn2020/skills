---
name: security-compliance-scanner
id: OC-0185
version: 1.0.0
description: "Security Compliance Scanner - Check skill scripts for hardcoded secrets or unsafe shell execution"
env: []
commands:
  - scan
  - scan-all
  - report
---

# Security Compliance Scanner

Scan skill scripts for security issues: hardcoded secrets, unsafe shell execution, dangerous builtins, insecure file operations, and other OWASP-relevant patterns.

## Prerequisites

- Python 3.8+

## Commands

| Command | Description |
|---------|-------------|
| `scan` | Scan a specific skill for security issues |
| `scan-all` | Scan all skills in the repository |
| `report` | Generate a markdown security compliance report |

## Usage

```bash
# Scan a specific skill
python3 scripts/security_compliance_scanner.py scan --skill gmail-triage

# Scan all skills and show summary
python3 scripts/security_compliance_scanner.py scan-all

# Scan a specific category
python3 scripts/security_compliance_scanner.py scan-all --category productivity

# Generate a full markdown compliance report
python3 scripts/security_compliance_scanner.py report --output security_report.md
```
