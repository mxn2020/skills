import { useState, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useSkills } from '../App';

// Sample blog posts - stored as data so adding new posts is easy
// In the future, these could be loaded from markdown files via a build script
const BLOG_POSTS = [
    {
        slug: 'introduction-to-agent-skills',
        title: 'Introduction to Agent Skills',
        date: '2026-02-22',
        author: 'Mehdi Nabhani',
        tags: ['agents', 'skills', 'open-source'],
        excerpt: 'A deep dive into what agent skills are, why they matter, and how this directory helps you build better AI agents.',
        readTime: '5 min read',
        content: `
# Introduction to Agent Skills

Agent skills are modular, reusable capabilities that extend what AI agents can do. Instead of building everything from scratch, you can compose skills together to create powerful agents.

## What is a Skill?

A skill is a self-contained unit of functionality that an agent can invoke. Each skill:

- Has a **clear purpose** — described in its \`SKILL.md\`
- Exposes **commands** — discrete actions the skill can perform
- Declares **dependencies** — environment variables and prerequisites
- Is **independently testable** — each skill can be verified in isolation

## Why This Directory?

With over **188 skills** across 14 categories, this directory serves as a central hub for discovering and integrating agent capabilities. Whether you need a GitHub integration, a budget tracker, or an AI image generator — there's likely a skill for that.

## How Skills Are Organized

Skills follow a hierarchical structure:

\`\`\`
skills/
├── cloud/
│   ├── devops/
│   │   ├── version-control/
│   │   │   ├── github-repo-manager/
│   │   │   │   ├── SKILL.md
│   │   │   │   └── scripts/
│   │   │   └── github-issues/
│   │   └── deployment/
├── ai/
│   ├── tools/
│   │   ├── rag-manager/
│   │   └── token-cost-estimator/
└── productivity/
    └── finance/
        ├── budget-tracker/
        └── stock-price-fetcher/
\`\`\`

Each \`SKILL.md\` contains YAML frontmatter with metadata, followed by documentation:

\`\`\`yaml
---
name: rag-manager
id: OC-0118
version: 1.0.0
description: "RAG Manager - Handle document chunking..."
env:
  - OPENAI_API_KEY
commands:
  - ingest
  - query
---
\`\`\`

## Getting Started

1. **Browse** the directory to find skills you need
2. **Read** the skill documentation to understand capabilities
3. **Integrate** by following the setup instructions
4. **Contribute** by adding your own skills — just create a folder!

---

*Built by [Mehdi Nabhani](https://the-mehdi.com) — find the source on [GitHub](https://github.com/mxn2020/skills).*
    `,
    },
    {
        slug: 'building-your-first-skill',
        title: 'Building Your First Skill',
        date: '2026-02-20',
        author: 'Mehdi Nabhani',
        tags: ['tutorial', 'getting-started'],
        excerpt: 'Step-by-step guide to creating a new skill for the directory. From folder structure to SKILL.md to scripts.',
        readTime: '8 min read',
        content: `
# Building Your First Skill

Creating a new skill for the directory is straightforward. This guide walks you through the entire process.

## Step 1: Choose a Category

Decide which category your skill belongs to. The current categories include:

| Category | Examples |
|----------|----------|
| AI | Image Gen, Voice Processing, RAG |
| Cloud | GitHub, AWS, Vercel, Stripe |
| Dev Tools | Skill Linter, Chaos Monkey |
| Productivity | Todoist, Linear, Gmail |
| Personal | Workout Logger, Smart Home |

## Step 2: Create the Folder

Create your skill folder inside the appropriate category:

\`\`\`bash
mkdir -p skills/ai/tools/my-awesome-skill/scripts
\`\`\`

## Step 3: Write the SKILL.md

Every skill needs a \`SKILL.md\` file with YAML frontmatter:

\`\`\`yaml
---
name: my-awesome-skill
id: OC-0200
version: 1.0.0
description: "My Awesome Skill - Does something amazing"
env:
  - MY_API_KEY
commands:
  - run
  - configure
  - test
---

# My Awesome Skill

Describe what your skill does here...
\`\`\`

## Step 4: Add Your Script

Create the main script in \`scripts/\`:

\`\`\`python
#!/usr/bin/env python3
"""My Awesome Skill - main entry point."""
import argparse

def main():
    parser = argparse.ArgumentParser(description="My Awesome Skill")
    subparsers = parser.add_subparsers(dest="command")

    # Add commands
    subparsers.add_parser("run", help="Run the skill")
    subparsers.add_parser("configure", help="Configure settings")
    subparsers.add_parser("test", help="Run self-test")

    args = parser.parse_args()
    # ... implement your logic

if __name__ == "__main__":
    main()
\`\`\`

## Step 5: Test & Submit

1. Run \`npm run build:index\` to verify your skill appears
2. Check the web app to see your skill card
3. Submit a pull request!

---

*That's it! Your skill is now part of the directory.*
    `,
    },
    {
        slug: 'skill-architecture-patterns',
        title: 'Skill Architecture Patterns',
        date: '2026-02-18',
        author: 'Mehdi Nabhani',
        tags: ['architecture', 'best-practices'],
        excerpt: 'Common patterns and best practices for structuring agent skills — from simple CLI wrappers to complex multi-step pipelines.',
        readTime: '6 min read',
        content: `
# Skill Architecture Patterns

After building 188+ skills, several patterns have emerged. Here are the most effective architectures for building robust agent skills.

## Pattern 1: CLI Wrapper

The simplest pattern — wrap an existing CLI tool:

\`\`\`
skill/
├── SKILL.md
└── scripts/
    └── wrapper.py    # Thin wrapper around 'gh', 'ffmpeg', etc.
\`\`\`

**When to use:** When a mature CLI already exists and you want to expose it to agents with better argument parsing.

## Pattern 2: API Client

Wrap a REST or GraphQL API:

\`\`\`
skill/
├── SKILL.md
└── scripts/
    ├── client.py     # API client with auth handling
    └── commands.py   # Individual command handlers
\`\`\`

**When to use:** For SaaS integrations (Stripe, Slack, Notion, etc.)

## Pattern 3: Pipeline

Chain multiple operations together:

\`\`\`
skill/
├── SKILL.md
└── scripts/
    ├── pipeline.py   # Orchestration logic
    ├── step_1.py     # Fetch/ingest
    ├── step_2.py     # Process/transform
    └── step_3.py     # Output/deliver
\`\`\`

**When to use:** For complex workflows like RAG ingestion, media processing, or data pipelines.

## Pattern 4: Local + Remote Hybrid

Some skills work both locally and with remote services:

\`\`\`
skill/
├── SKILL.md
└── scripts/
    ├── main.py       # Entry point with --local/--remote flag
    ├── local.py      # Local processing (e.g., FFmpeg)
    └── remote.py     # API-based processing
\`\`\`

**When to use:** When you want offline capabilities with optional cloud enhancement.

## Best Practices

1. **Single responsibility** — one skill, one domain
2. **Clear commands** — each command does one thing well
3. **Environment variables** — never hardcode secrets
4. **Error handling** — graceful failures with clear messages
5. **Documentation** — comprehensive SKILL.md with examples

---

*These patterns have been refined across 188+ skills. Use them as starting points, not rigid rules.*
    `,
    },
];

function BlogList() {
    const [selectedTag, setSelectedTag] = useState(null);

    const allTags = useMemo(() => {
        const tags = new Set();
        BLOG_POSTS.forEach(p => p.tags.forEach(t => tags.add(t)));
        return Array.from(tags).sort();
    }, []);

    const filtered = selectedTag
        ? BLOG_POSTS.filter(p => p.tags.includes(selectedTag))
        : BLOG_POSTS;

    return (
        <div className="page-container">
            <div className="blog-header animate-in">
                <div className="hero-badge">📝 Blog</div>
                <h1>
                    Thoughts on <span className="gradient-text">AI Agents</span>
                </h1>
                <p className="hero-subtitle">
                    Tutorials, architecture patterns, and insights on building agent skills.
                </p>
            </div>

            {/* Tags filter */}
            <div className="blog-tags animate-in animate-in-delay-1">
                <button
                    className={`blog-tag ${!selectedTag ? 'active' : ''}`}
                    onClick={() => setSelectedTag(null)}
                >
                    All
                </button>
                {allTags.map(tag => (
                    <button
                        key={tag}
                        className={`blog-tag ${selectedTag === tag ? 'active' : ''}`}
                        onClick={() => setSelectedTag(tag)}
                    >
                        {tag}
                    </button>
                ))}
            </div>

            {/* Post list */}
            <div className="blog-posts animate-in animate-in-delay-2">
                {filtered.map(post => (
                    <Link to={`/blog/${post.slug}`} key={post.slug} className="blog-post-card">
                        <div className="blog-post-meta">
                            <span className="blog-post-date">{new Date(post.date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</span>
                            <span className="blog-post-dot">·</span>
                            <span className="blog-post-read">{post.readTime}</span>
                        </div>
                        <h2 className="blog-post-title">{post.title}</h2>
                        <p className="blog-post-excerpt">{post.excerpt}</p>
                        <div className="blog-post-tags">
                            {post.tags.map(tag => (
                                <span key={tag} className="blog-post-tag">{tag}</span>
                            ))}
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    );
}

function BlogDetail({ slug }) {
    const post = BLOG_POSTS.find(p => p.slug === slug);

    if (!post) {
        return (
            <div className="page-container">
                <div className="empty-state">
                    <div className="empty-state-icon">📝</div>
                    <h3>Post not found</h3>
                    <Link to="/blog" className="back-link">← Back to Blog</Link>
                </div>
            </div>
        );
    }

    return (
        <div className="page-container">
            <div className="breadcrumb">
                <Link to="/">Home</Link>
                <span className="breadcrumb-sep">/</span>
                <Link to="/blog">Blog</Link>
                <span className="breadcrumb-sep">/</span>
                <span className="breadcrumb-current">{post.title}</span>
            </div>

            <article className="blog-article animate-in">
                <div className="blog-article-header">
                    <div className="blog-post-meta">
                        <span className="blog-post-date">
                            {new Date(post.date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
                        </span>
                        <span className="blog-post-dot">·</span>
                        <span className="blog-post-read">{post.readTime}</span>
                        <span className="blog-post-dot">·</span>
                        <span className="blog-post-author">By {post.author}</span>
                    </div>
                    <div className="blog-post-tags" style={{ marginTop: 16 }}>
                        {post.tags.map(tag => (
                            <span key={tag} className="blog-post-tag">{tag}</span>
                        ))}
                    </div>
                </div>

                <div className="markdown-body">
                    <Markdown remarkPlugins={[remarkGfm]}>{post.content}</Markdown>
                </div>
            </article>
        </div>
    );
}

export default function BlogPage() {
    const { slug } = useParams();

    if (slug) {
        return <BlogDetail slug={slug} />;
    }

    return <BlogList />;
}
