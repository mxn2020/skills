#!/usr/bin/env node
/**
 * build-index.js
 *
 * Recursively scans the skills repo for SKILL.md files, parses YAML
 * frontmatter, and outputs a single skills-index.json used by the web app.
 *
 * Usage: node scripts/build-index.js
 */

import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { globSync } from 'glob';

const REPO_ROOT = path.resolve(import.meta.dirname, '..', '..');
const OUT_FILE = path.resolve(import.meta.dirname, '..', 'public', 'skills-index.json');

// Directories to skip
const IGNORE = new Set(['.git', '.claude', 'node_modules', 'website', 'examples']);

function slugToTitle(slug) {
  return slug
    .split('-')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

// Category icons (emoji mapping)
const CATEGORY_ICONS = {
  'ai': '🤖',
  'cloud': '☁️',
  'dev-tools': '🧪',
  'personal': '🏠',
  'productivity': '📋',
};

function buildIndex() {
  // Find all SKILL.md files
  const pattern = path.join(REPO_ROOT, '**', 'SKILL.md');
  const files = globSync(pattern, { ignore: ['**/node_modules/**', '**/website/**'] });

  const categoryMap = new Map();
  let totalSkills = 0;

  for (const filepath of files) {
    const raw = fs.readFileSync(filepath, 'utf-8');
    const { data: frontmatter, content: markdownBody } = matter(raw);

    // Get the relative path from repo root
    const relDir = path.relative(REPO_ROOT, path.dirname(filepath));
    const parts = relDir.split(path.sep);

    // Skip ignored directories
    if (IGNORE.has(parts[0])) continue;

    // Determine the category hierarchy
    // e.g. "cloud/devops/version-control/github-repo-manager" ->
    //   category = "cloud", subcategory = "devops/version-control", skill folder = "github-repo-manager"
    // e.g. "ai/tools/rag-manager" ->
    //   category = "ai", subcategory = "tools", skill folder = "rag-manager"

    let categorySlug, subcategorySlug, skillSlug;

    if (parts.length === 1) {
      // SKILL.md directly in a top-level directory
      categorySlug = parts[0];
      subcategorySlug = null;
      skillSlug = parts[0];
    } else if (parts.length === 2) {
      // category/skill (e.g. "ai/rag-manager")
      categorySlug = parts[0];
      subcategorySlug = null;
      skillSlug = parts[1];
    } else if (parts.length >= 3) {
      // category/[subcategory...]/skill — join middle parts as subcategory
      categorySlug = parts[0];
      subcategorySlug = parts.slice(1, -1).join('/');
      skillSlug = parts[parts.length - 1];
    }

    const skill = {
      slug: skillSlug,
      name: frontmatter.name || skillSlug,
      id: frontmatter.id || null,
      version: frontmatter.version || '1.0.0',
      description: (frontmatter.description || '').trim(),
      commands: frontmatter.commands || [],
      env: frontmatter.env || [],
      path: relDir,
      markdownBody: markdownBody.trim(),
    };

    // Build category structure
    if (!categoryMap.has(categorySlug)) {
      categoryMap.set(categorySlug, {
        slug: categorySlug,
        name: slugToTitle(categorySlug),
        icon: CATEGORY_ICONS[categorySlug] || '📦',
        subcategories: new Map(),
        skills: [],
      });
    }

    const category = categoryMap.get(categorySlug);

    if (subcategorySlug) {
      if (!category.subcategories.has(subcategorySlug)) {
        category.subcategories.set(subcategorySlug, {
          slug: subcategorySlug,
          name: slugToTitle(subcategorySlug),
          skills: [],
        });
      }
      category.subcategories.get(subcategorySlug).skills.push(skill);
    } else {
      category.skills.push(skill);
    }

    totalSkills++;
  }

  // Convert maps to arrays and sort
  const categories = Array.from(categoryMap.values())
    .map(cat => ({
      ...cat,
      subcategories: Array.from(cat.subcategories.values()).sort((a, b) =>
        a.name.localeCompare(b.name)
      ),
      skillCount:
        cat.skills.length +
        Array.from(cat.subcategories.values()).reduce((sum, sc) => sum + sc.skills.length, 0),
    }))
    .sort((a, b) => b.skillCount - a.skillCount);

  const index = {
    categories,
    totalSkills,
    generatedAt: new Date().toISOString(),
  };

  // Ensure output dir exists
  const outDir = path.dirname(OUT_FILE);
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  fs.writeFileSync(OUT_FILE, JSON.stringify(index, null, 2));
  console.log(`✅ Built skills index: ${totalSkills} skills across ${categories.length} categories`);
  console.log(`   → ${OUT_FILE}`);
}

buildIndex();
