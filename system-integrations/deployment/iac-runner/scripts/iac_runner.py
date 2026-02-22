#!/usr/bin/env python3
"""Pulumi/Terraform Runner – OC-0024"""

import argparse
import subprocess
import sys

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def _run(cmd, cwd=None):
    print(f"{YELLOW}> {' '.join(cmd)}{RESET}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print(f"{RED}Error (exit {result.returncode}):{RESET}")
        if result.stderr:
            print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()


def tf_init(args):
    _run(["terraform", "init"], cwd=args.dir)
    print(f"{GREEN}Terraform initialized in {args.dir}{RESET}")


def tf_plan(args):
    cmd = ["terraform", "plan"]
    if args.var_file:
        cmd += [f"-var-file={args.var_file}"]
    _run(cmd, cwd=args.dir)


def tf_apply(args):
    cmd = ["terraform", "apply"]
    if args.auto_approve:
        cmd.append("-auto-approve")
    if args.var_file:
        cmd += [f"-var-file={args.var_file}"]
    _run(cmd, cwd=args.dir)
    print(f"{GREEN}Terraform apply complete{RESET}")


def tf_destroy(args):
    cmd = ["terraform", "destroy"]
    if args.auto_approve:
        cmd.append("-auto-approve")
    _run(cmd, cwd=args.dir)
    print(f"{GREEN}Terraform destroy complete{RESET}")


def tf_list_stacks(args):
    _run(["terraform", "workspace", "list"], cwd=args.dir)


def pu_init(args):
    _run(["pulumi", "stack", "init", args.stack or "dev"], cwd=args.dir)
    print(f"{GREEN}Pulumi stack initialized{RESET}")


def pu_plan(args):
    cmd = ["pulumi", "preview"]
    if args.stack:
        cmd += ["--stack", args.stack]
    _run(cmd, cwd=args.dir)


def pu_apply(args):
    cmd = ["pulumi", "up"]
    if args.auto_approve:
        cmd.append("--yes")
    if args.stack:
        cmd += ["--stack", args.stack]
    _run(cmd, cwd=args.dir)
    print(f"{GREEN}Pulumi up complete{RESET}")


def pu_destroy(args):
    cmd = ["pulumi", "destroy"]
    if args.auto_approve:
        cmd.append("--yes")
    if args.stack:
        cmd += ["--stack", args.stack]
    _run(cmd, cwd=args.dir)
    print(f"{GREEN}Pulumi destroy complete{RESET}")


def pu_list_stacks(args):
    _run(["pulumi", "stack", "ls"], cwd=args.dir)


def main():
    parser = argparse.ArgumentParser(description="Pulumi/Terraform Runner")
    parser.add_argument("--tool", choices=["terraform", "pulumi"], required=True)

    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize workspace")
    p_init.add_argument("--dir", default=".")
    p_init.add_argument("--stack", default=None, help="Pulumi stack name")

    p_plan = sub.add_parser("plan", help="Preview changes")
    p_plan.add_argument("--dir", default=".")
    p_plan.add_argument("--stack", default=None)
    p_plan.add_argument("--var-file", default=None)

    p_apply = sub.add_parser("apply", help="Apply changes")
    p_apply.add_argument("--dir", default=".")
    p_apply.add_argument("--stack", default=None)
    p_apply.add_argument("--auto-approve", action="store_true")
    p_apply.add_argument("--var-file", default=None)

    p_destroy = sub.add_parser("destroy", help="Destroy resources")
    p_destroy.add_argument("--dir", default=".")
    p_destroy.add_argument("--stack", default=None)
    p_destroy.add_argument("--auto-approve", action="store_true")

    p_stacks = sub.add_parser("list-stacks", help="List stacks/workspaces")
    p_stacks.add_argument("--dir", default=".")

    args = parser.parse_args()

    dispatch = {
        "terraform": {
            "init": tf_init,
            "plan": tf_plan,
            "apply": tf_apply,
            "destroy": tf_destroy,
            "list-stacks": tf_list_stacks,
        },
        "pulumi": {
            "init": pu_init,
            "plan": pu_plan,
            "apply": pu_apply,
            "destroy": pu_destroy,
            "list-stacks": pu_list_stacks,
        },
    }
    dispatch[args.tool][args.command](args)


if __name__ == "__main__":
    main()
