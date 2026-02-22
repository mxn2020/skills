#!/usr/bin/env python3
"""
Obsidian Note Creator — OC-0154
Write structured markdown notes directly into an Obsidian vault.
"""

import os
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _vault() -> Path:
    vault_path = os.environ.get("OBSIDIAN_VAULT_PATH", "")
    if not vault_path:
        _die("OBSIDIAN_VAULT_PATH is not set.")
    path = Path(vault_path).expanduser()
    if not path.exists():
        _die(f"Vault path does not exist: {path}")
    return path


def _sanitize_filename(title: str) -> str:
    """Remove chars invalid in filenames."""
    invalid = r'\/:*?"<>|'
    for ch in invalid:
        title = title.replace(ch, "-")
    return title.strip()


def _build_frontmatter(title: str, tags: str = "", created: str = "") -> str:
    lines = ["---"]
    lines.append(f"title: {title}")
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        lines.append("tags:")
        for tag in tag_list:
            lines.append(f"  - {tag}")
    lines.append(f"created: {created or datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    lines.append("---\n")
    return "\n".join(lines)


def create_note(title: str, content: str = "", tags: str = "",
                folder: str = "", link: str = ""):
    vault = _vault()
    safe_title = _sanitize_filename(title)
    target_dir = vault / folder if folder else vault
    target_dir.mkdir(parents=True, exist_ok=True)

    note_path = target_dir / f"{safe_title}.md"
    if note_path.exists():
        print(f"{YELLOW}Note already exists: {note_path}{RESET}")
        return

    frontmatter = _build_frontmatter(title, tags)
    body = f"# {title}\n\n{content}"
    if link:
        body += f"\n\n## Related\n- [[{link}]]"

    note_path.write_text(frontmatter + body, encoding="utf-8")
    print(f"{GREEN}Note created: {note_path}{RESET}")
    if tags:
        print(f"  Tags: {tags}")
    print()


def create_daily(template: str = ""):
    vault = _vault()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    daily_dir = vault / "Daily Notes"
    daily_dir.mkdir(exist_ok=True)

    note_path = daily_dir / f"{today}.md"
    if note_path.exists():
        print(f"{YELLOW}Daily note already exists: {note_path}{RESET}")
        return

    sections = []
    if "tasks" in template:
        sections.append("## Tasks\n- [ ] \n- [ ] \n- [ ] ")
    if "journal" in template:
        sections.append("## Journal\n\n")
    if "meetings" in template:
        sections.append("## Meetings\n\n")
    if not sections:
        sections = ["## Daily Notes\n\n", "## Tasks\n- [ ] \n", "## Reflections\n\n"]

    body = f"---\ndate: {today}\ntype: daily\n---\n\n# {today}\n\n"
    body += "\n\n".join(sections)

    note_path.write_text(body, encoding="utf-8")
    print(f"{GREEN}Daily note created: {note_path}{RESET}")
    print()


def search_notes(query: str, max_results: int = 20):
    vault = _vault()
    query_lower = query.lower()
    results = []

    for md_file in vault.rglob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8", errors="ignore")
            if query_lower in text.lower():
                # Find first matching line
                for i, line in enumerate(text.splitlines(), 1):
                    if query_lower in line.lower():
                        results.append((md_file, i, line.strip()))
                        break
        except OSError:
            continue

    if not results:
        print(f"{YELLOW}No notes found containing '{query}'.{RESET}")
        return

    print(f"\n{GREEN}Found {len(results)} note(s) matching '{query}':{RESET}\n")
    for path, lineno, snippet in results[:max_results]:
        rel_path = path.relative_to(vault)
        print(f"  {CYAN}{rel_path}{RESET}  (line {lineno})")
        print(f"    {snippet[:80]}")
    print()


def append_to_note(title: str, content: str, folder: str = ""):
    vault = _vault()
    safe_title = _sanitize_filename(title)
    search_dirs = [vault / folder] if folder else [vault]

    note_path = None
    for d in search_dirs:
        p = d / f"{safe_title}.md"
        if p.exists():
            note_path = p
            break

    if not note_path:
        # Search recursively
        matches = list(vault.rglob(f"{safe_title}.md"))
        if matches:
            note_path = matches[0]

    if not note_path:
        _die(f"Note '{title}' not found in vault.")

    with open(note_path, "a", encoding="utf-8") as f:
        f.write(f"\n{content}\n")

    print(f"{GREEN}Appended to: {note_path.relative_to(vault)}{RESET}")
    print()


def list_notes(folder: str = "", limit: int = 30):
    vault = _vault()
    target = vault / folder if folder else vault

    if not target.exists():
        _die(f"Folder '{folder}' not found in vault.")

    notes = sorted(target.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not notes:
        print(f"{YELLOW}No notes found in '{folder or 'vault root'}'.{RESET}")
        return

    print(f"\n{BOLD}Notes in '{folder or 'vault root'}' ({len(notes)} total):{RESET}\n")
    for note in notes[:limit]:
        size = note.stat().st_size
        mtime = datetime.fromtimestamp(note.stat().st_mtime).strftime("%Y-%m-%d")
        print(f"  {CYAN}{note.stem}{RESET}  ({size}B, modified {mtime})")
    if len(notes) > limit:
        print(f"  ... and {len(notes) - limit} more")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="obsidian_creator.py",
        description="Obsidian Note Creator — OC-0154"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("create-note", help="Create a new note")
    p.add_argument("--title", required=True)
    p.add_argument("--content", default="")
    p.add_argument("--tags", default="", help="Comma-separated tags")
    p.add_argument("--folder", default="", help="Subfolder in vault")
    p.add_argument("--link", default="", help="Related note to backlink")

    p = sub.add_parser("create-daily", help="Create today's daily note")
    p.add_argument("--template", default="tasks,journal",
                   help="Sections: tasks,journal,meetings (comma-separated)")

    p = sub.add_parser("search-notes", help="Search notes by keyword")
    p.add_argument("--query", required=True)
    p.add_argument("--max-results", type=int, default=20)

    p = sub.add_parser("append-to-note", help="Append content to a note")
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--folder", default="")

    p = sub.add_parser("list-notes", help="List notes in a folder")
    p.add_argument("--folder", default="")
    p.add_argument("--limit", type=int, default=30)

    args = parser.parse_args()
    dispatch = {
        "create-note":    lambda: create_note(args.title, args.content, args.tags,
                                               args.folder, args.link),
        "create-daily":   lambda: create_daily(args.template),
        "search-notes":   lambda: search_notes(args.query, args.max_results),
        "append-to-note": lambda: append_to_note(args.title, args.content, args.folder),
        "list-notes":     lambda: list_notes(args.folder, args.limit),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
