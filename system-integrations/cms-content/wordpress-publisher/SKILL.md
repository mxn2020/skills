---
name: WordPress Post Publisher
id: OC-0046
version: 1.0.0
description: Draft and publish blog posts via the WordPress REST API.
---

# WordPress Post Publisher

Create, update, and manage WordPress posts and categories through the REST API.

## Capabilities

- List, create, update, and delete posts
- Manage post status (draft, publish, pending)
- Browse categories for content organization

## Quick Start

```bash
export WORDPRESS_URL="https://your-site.com"
export WORDPRESS_USERNAME="admin"
export WORDPRESS_APP_PASSWORD="xxxx xxxx xxxx xxxx"
python3 scripts/wordpress_publisher.py list-posts
python3 scripts/wordpress_publisher.py create-post --title "Hello World" --content "<p>My first post</p>"
```

## Commands & Parameters

| Command           | Parameters                                             | Description                     |
| ----------------- | ------------------------------------------------------ | ------------------------------- |
| `list-posts`      | `--status` (optional), `--per-page` (optional)         | List posts                      |
| `get-post`        | `--id`                                                 | Get a single post               |
| `create-post`     | `--title`, `--content`, `--status` (default: draft)    | Create a new post               |
| `update-post`     | `--id`, `--title`/`--content`/`--status` (optional)    | Update an existing post         |
| `delete-post`     | `--id`                                                 | Move a post to trash            |
| `list-categories` | —                                                      | List all categories             |

## Dependencies

- Python 3.8+
- `requests` library
- Environment variables: `WORDPRESS_URL`, `WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD`
