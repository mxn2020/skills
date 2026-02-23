---
name: github-repo-manager
id: OC-0001
version: 1.0.0
description: GitHub Repo Manager. Create, list, delete repos; manage collaborators. Use when user asks to manage GitHub repositories or collaborators.
---

# GitHub Repo Manager

Create, list, delete GitHub repositories and manage collaborator access from the command line.

## Capabilities

1. **List Repos**: List repos for the authenticated user or an organization.
2. **Create Repo**: Create a new public or private repository.
3. **Delete Repo**: Delete a repository (requires confirmation).
4. **Get Info**: Show metadata for a specific repository.
5. **Add Collaborator**: Add a collaborator with a specified permission level.
6. **Remove Collaborator**: Remove a collaborator from a repository.
7. **List Collaborators**: List all collaborators and their permissions.

## Quick Start

```bash
# List your repositories
python3 skills/system-integrations/version-control/github-repo-manager/scripts/repo_manager.py list-repos

# Create a new private repo
python3 skills/system-integrations/version-control/github-repo-manager/scripts/repo_manager.py create-repo --name my-project --private --description "My new project"

# Add a collaborator
python3 skills/system-integrations/version-control/github-repo-manager/scripts/repo_manager.py add-collaborator --repo owner/my-project --user johndoe --permission write
```

## Commands & Parameters

### `list-repos`
Lists repositories for the authenticated user or an org.
- `--org`: Organization name (optional; defaults to authenticated user)
- `--limit`: Max repos to return (default: 30)
- `--visibility`: Filter by visibility: public, private, all (default: all)

### `create-repo`
Creates a new repository.
- `--name`: Repository name (required)
- `--description`: Short description
- `--private`: Make the repo private (flag)
- `--org`: Create under an organization instead of personal account

### `delete-repo`
Deletes a repository. Prompts for confirmation unless `--confirm` is passed.
- `--repo`: Repository (owner/name) (required)
- `--confirm`: Skip interactive confirmation (flag)

### `get-info`
Shows metadata for a repository.
- `--repo`: Repository (owner/name) (required)

### `add-collaborator`
Adds a collaborator with a given permission level.
- `--repo`: Repository (owner/name) (required)
- `--user`: GitHub username to add (required)
- `--permission`: Permission level: pull, push, maintain, triage, admin (default: push)

### `remove-collaborator`
Removes a collaborator from a repository.
- `--repo`: Repository (owner/name) (required)
- `--user`: GitHub username to remove (required)

### `list-collaborators`
Lists all collaborators in a repository.
- `--repo`: Repository (owner/name) (required)

## Dependencies
- `gh` CLI installed and authenticated.
- `GITHUB_TOKEN` environment variable (or `gh auth login`).
