---
name: changelog-generator
version: 1.0.0
description: Changelog Generator. Auto-generate changelogs from commit history and PR titles. Use when user asks to generate, preview, or update a CHANGELOG.md file.
---

# Changelog Generator

Automatically generate changelogs from git commit history and merged PR titles.

## Capabilities

1. **Generate**: Create a full CHANGELOG.md from git history and PR titles.
2. **Preview**: Preview changelog output without writing to file.
3. **Append**: Append a new version section to an existing CHANGELOG.md.

## Quick Start

```bash
# Generate a changelog
python3 skills/system-integrations/version-control/changelog-generator/scripts/changelog.py generate --repo owner/repo

# Preview without writing
python3 skills/system-integrations/version-control/changelog-generator/scripts/changelog.py preview --repo owner/repo --since v1.0.0

# Append a new version
python3 skills/system-integrations/version-control/changelog-generator/scripts/changelog.py append --repo owner/repo --version 1.2.0 --since v1.1.0
```

## Commands & Parameters

### `generate`
Generates a full CHANGELOG.md from git log and merged PRs.
- `--repo`: Repository (owner/name) (required)
- `--output`: Output file path (default: CHANGELOG.md)
- `--since`: Start from tag/ref (optional, generates from all history if omitted)
- `--group-by`: Group entries by type (default: type)

### `preview`
Previews changelog output to stdout without writing.
- `--repo`: Repository (owner/name) (required)
- `--since`: Start from tag/ref
- `--group-by`: Group entries by type (default: type)

### `append`
Appends a new version section to existing CHANGELOG.md.
- `--repo`: Repository (owner/name) (required)
- `--version`: Version string for the new section (required)
- `--since`: Start from tag/ref (required)
- `--output`: Output file path (default: CHANGELOG.md)

## Dependencies
- `gh` CLI installed and authenticated.
- `git` CLI available (for local commit history).
- `GITHUB_TOKEN` environment variable (or `gh auth login`).
