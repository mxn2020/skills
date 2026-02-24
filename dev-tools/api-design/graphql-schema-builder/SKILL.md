---
name: graphql-schema-builder
id: OC-0200
version: 1.0.0
description: "Scaffold GraphQL schemas and basic resolvers from database schemas or descriptions."
env:
  - OPENAI_API_KEY
commands:
  - scaffold-schema
  - generate-resolvers
---

# GraphQL Schema Builder

Scaffold GraphQL schemas and basic resolvers from database schemas or natural language descriptions.

## Prerequisites
- A valid `OPENAI_API_KEY` environment variable.

## Commands
| Command              | Description                              |
|----------------------|------------------------------------------|
| `scaffold-schema`    | Generate a GraphQL schema definitions file (`.graphql`) |
| `generate-resolvers` | Generate basic resolver boilerplate for a given schema |

## Usage
```bash
export OPENAI_API_KEY="sk-..."
python3 scripts/graphql_schema_builder.py scaffold-schema --prompt "A blog with Posts, Authors, and Comments" --output schema.graphql
python3 scripts/graphql_schema_builder.py generate-resolvers --schema schema.graphql --output resolvers.js
```
