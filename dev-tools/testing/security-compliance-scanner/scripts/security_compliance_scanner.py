#!/usr/bin/env python3
"""
Security Compliance Scanner — OC-0185
Check skill scripts for hardcoded secrets, unsafe shell execution, and security anti-patterns.
"""

import re
import sys
import ast
import argparse
import datetime
from pathlib import Path

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

# ── Security rules ──────────────────────────────────────────────────────────
# Each rule: (severity, rule_id, description, regex_pattern)
RULES = [
    # Hardcoded secrets
    ("CRITICAL", "SEC-001", "Hardcoded password",
     r'password\s*=\s*["\'][^"\']{4,}["\']'),
    ("CRITICAL", "SEC-002", "Hardcoded API key (generic)",
     r'api[_-]?key\s*=\s*["\'][a-zA-Z0-9_\-]{20,}["\']'),
    ("CRITICAL", "SEC-003", "Hardcoded secret / token",
     r'(secret|token|auth)\s*=\s*["\'][a-zA-Z0-9_\-\.]{20,}["\']'),
    ("CRITICAL", "SEC-004", "AWS access key ID pattern",
     r'AKIA[0-9A-Z]{16}'),
    ("CRITICAL", "SEC-005", "Private key block",
     r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    ("HIGH",     "SEC-006", "Hardcoded Bearer token",
     r'Bearer\s+[a-zA-Z0-9_\-\.]{20,}'),
    # Unsafe execution
    ("HIGH",     "SEC-010", "os.system() usage — prefer subprocess",
     r'\bos\.system\s*\('),
    ("HIGH",     "SEC-011", "eval() usage",
     r'\beval\s*\('),
    ("HIGH",     "SEC-012", "exec() usage",
     r'\bexec\s*\('),
    ("HIGH",     "SEC-013", "subprocess with shell=True and user input",
     r'subprocess\.(run|call|Popen).*shell\s*=\s*True'),
    ("MEDIUM",   "SEC-014", "pickle.loads() — deserialization risk",
     r'\bpickle\.loads?\s*\('),
    ("MEDIUM",   "SEC-015", "yaml.load() without Loader — use yaml.safe_load()",
     r'\byaml\.load\s*\([^)]*\)(?!.*Loader)'),
    # Path traversal
    ("HIGH",     "SEC-020", "Potential path traversal via string concat",
     r'open\s*\(\s*[^)]*\+'),
    ("MEDIUM",   "SEC-021", "os.path.join with user-controlled input",
     r'os\.path\.join\s*\([^)]*args\.[a-z]'),
    # Network
    ("MEDIUM",   "SEC-030", "SSL verification disabled",
     r'verify\s*=\s*False'),
    ("MEDIUM",   "SEC-031", "Hardcoded HTTP URL (prefer HTTPS)",
     r'http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)[a-zA-Z0-9]'),
    # Debug / information disclosure
    ("LOW",      "SEC-040", "print() of sensitive variable names",
     r'print\s*\([^)]*(?:password|secret|token|key)[^)]*\)'),
    ("LOW",      "SEC-041", "TODO / FIXME with security note",
     r'#\s*(TODO|FIXME|HACK|XXX).*(?:security|secret|auth|token)'),
]

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
SEVERITY_COLORS = {
    "CRITICAL": RED + BOLD,
    "HIGH":     RED,
    "MEDIUM":   YELLOW,
    "LOW":      CYAN,
}


def _skills_root() -> Path:
    script = Path(__file__).resolve()
    root = script.parent.parent.parent.parent
    if (root / "IDEAS.md").exists():
        return root
    cwd = Path.cwd()
    while cwd != cwd.parent:
        if (cwd / "IDEAS.md").exists():
            return cwd
        cwd = cwd.parent
    return root


def _find_skill(skill_name: str) -> Path:
    root = _skills_root()
    matches = list(root.rglob(f"{skill_name}/SKILL.md"))
    if not matches:
        print(f"{RED}Skill '{skill_name}' not found.{RESET}")
        sys.exit(1)
    return matches[0].parent


def _scan_file(file_path: Path) -> list:
    """Return list of (line_no, severity, rule_id, description, matched_text)."""
    findings = []
    try:
        code = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings

    for severity, rule_id, desc, pattern in RULES:
        for m in re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE):
            # Determine line number
            line_no = code[:m.start()].count("\n") + 1
            snippet = m.group(0)[:80].replace("\n", "↵")
            findings.append((line_no, severity, rule_id, desc, snippet))

    # AST-based check: detect hardcoded string assigned to env-like names
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name_lower = target.id.lower()
                        if any(kw in name_lower for kw in ("password", "secret", "api_key", "token", "auth")):
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                val = node.value.value
                                if len(val) >= 8 and val not in ("", "your_token", "your_key", "changeme"):
                                    findings.append((
                                        node.lineno, "CRITICAL", "SEC-099",
                                        f"AST: hardcoded value in '{target.id}'",
                                        repr(val[:40])
                                    ))
    except SyntaxError:
        pass

    # Sort by severity then line number
    findings.sort(key=lambda x: (SEVERITY_ORDER.get(x[1], 9), x[0]))
    return findings


def scan_skill(skill_path: Path) -> dict:
    scripts_dir = skill_path / "scripts"
    all_findings = {}
    if scripts_dir.exists():
        for py_file in sorted(scripts_dir.glob("*.py")):
            findings = _scan_file(py_file)
            if findings:
                all_findings[py_file.name] = findings
    return all_findings


def _severity_of(findings_dict: dict) -> str:
    """Return highest severity across all findings."""
    worst = "CLEAN"
    for findings in findings_dict.values():
        for _, sev, *_ in findings:
            if SEVERITY_ORDER.get(sev, 9) < SEVERITY_ORDER.get(worst, 9):
                worst = sev
    return worst


def scan(skill_name: str):
    skill_path = _find_skill(skill_name)
    all_findings = scan_skill(skill_path)

    print(f"\n{BOLD}Security Scan — {skill_name}{RESET}\n")
    if not all_findings:
        print(f"  {GREEN}✓ No security issues found.{RESET}\n")
        return

    for filename, findings in all_findings.items():
        print(f"  {CYAN}{filename}{RESET}")
        for line_no, severity, rule_id, desc, snippet in findings:
            color = SEVERITY_COLORS.get(severity, RESET)
            print(f"    {color}[{severity}]{RESET}  L{line_no}  {rule_id}  {desc}")
            print(f"           {YELLOW}{snippet}{RESET}")
        print()

    worst = _severity_of(all_findings)
    total = sum(len(v) for v in all_findings.values())
    color = SEVERITY_COLORS.get(worst, RESET)
    print(f"  {total} finding(s) — worst: {color}{worst}{RESET}\n")


def scan_all(category: str = None):
    root = _skills_root()
    all_skill_mds = list(root.rglob("SKILL.md"))
    if category:
        all_skill_mds = [p for p in all_skill_mds if category.lower() in str(p).lower()]

    clean = critical = high = medium = low = 0
    print(f"\n{BOLD}Security Scan — All Skills{' (' + category + ')' if category else ''}{RESET}\n")

    for skill_md in sorted(all_skill_mds):
        skill_path = skill_md.parent
        skill_name = skill_path.name
        findings = scan_skill(skill_path)
        worst = _severity_of(findings)
        count = sum(len(v) for v in findings.values())

        if worst == "CLEAN":
            clean += 1
            print(f"  {GREEN}✓{RESET}  {skill_name}")
        else:
            color = SEVERITY_COLORS.get(worst, RESET)
            print(f"  {color}✗{RESET}  {skill_name}  [{color}{worst}{RESET}]  {count} finding(s)")
            if worst == "CRITICAL": critical += 1
            elif worst == "HIGH":   high += 1
            elif worst == "MEDIUM": medium += 1
            else:                   low += 1

    total = clean + critical + high + medium + low
    print(f"\n  {BOLD}Results:{RESET} {total} skills scanned")
    print(f"    {GREEN}✓ Clean:    {clean}{RESET}")
    print(f"    {SEVERITY_COLORS['CRITICAL']}✗ Critical: {critical}{RESET}")
    print(f"    {SEVERITY_COLORS['HIGH']}✗ High:     {high}{RESET}")
    print(f"    {SEVERITY_COLORS['MEDIUM']}! Medium:   {medium}{RESET}")
    print(f"    {SEVERITY_COLORS['LOW']}· Low:      {low}{RESET}")
    print()


def report(output: str = None):
    root = _skills_root()
    all_skill_mds = list(root.rglob("SKILL.md"))
    lines = ["# OpenClaw Skills — Security Compliance Report\n\n"]
    lines.append(f"Generated: {datetime.datetime.utcnow().isoformat()}Z\n\n")
    lines.append("---\n\n")

    total_findings = 0
    skills_with_issues = 0

    for skill_md in sorted(all_skill_mds):
        skill_path = skill_md.parent
        skill_name = skill_path.name
        findings = scan_skill(skill_path)
        if not findings:
            continue
        skills_with_issues += 1
        count = sum(len(v) for v in findings.values())
        total_findings += count
        worst = _severity_of(findings)
        lines.append(f"## {skill_name} — {worst} ({count} finding(s))\n\n")
        for filename, file_findings in findings.items():
            lines.append(f"### `{filename}`\n\n")
            for line_no, severity, rule_id, desc, snippet in file_findings:
                icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵"}.get(severity, "⚪")
                lines.append(f"- {icon} **{severity}** `{rule_id}` L{line_no}: {desc}\n")
                lines.append(f"  ```\n  {snippet}\n  ```\n")
        lines.append("\n")

    lines.append("---\n\n")
    lines.append(f"**Total:** {total_findings} finding(s) across {skills_with_issues} skill(s)\n")
    content = "".join(lines)

    if output:
        Path(output).write_text(content, encoding="utf-8")
        print(f"{GREEN}Report saved to: {output}{RESET}")
        print(f"  {total_findings} finding(s) across {skills_with_issues} skill(s)")
    else:
        print(content)


def main():
    parser = argparse.ArgumentParser(
        prog="security_compliance_scanner.py",
        description="Security Compliance Scanner — OC-0185"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("scan", help="Scan a specific skill")
    p.add_argument("--skill", required=True)

    p = sub.add_parser("scan-all", help="Scan all skills")
    p.add_argument("--category", default=None)

    p = sub.add_parser("report", help="Generate markdown compliance report")
    p.add_argument("--output", default=None, help="Save report to file")

    args = parser.parse_args()
    if args.cmd == "scan":
        scan(args.skill)
    elif args.cmd == "scan-all":
        scan_all(args.category)
    elif args.cmd == "report":
        report(args.output)


if __name__ == "__main__":
    main()
