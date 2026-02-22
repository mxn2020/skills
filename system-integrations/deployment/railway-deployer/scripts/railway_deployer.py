#!/usr/bin/env python3
"""Railway Project Deployer – OC-0011"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

GQL_URL = "https://backboard.railway.app/graphql/v2"


def _headers():
    token = os.environ.get("RAILWAY_TOKEN")
    if not token:
        print(f"{RED}Error: RAILWAY_TOKEN is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _gql(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    resp = requests.post(GQL_URL, headers=_headers(), json=payload)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    data = resp.json()
    if "errors" in data:
        print(f"{RED}GraphQL errors: {json.dumps(data['errors'])}{RESET}")
        sys.exit(1)
    return data.get("data", {})


def list_projects(args):
    query = "query { me { projects { edges { node { id name } } } } }"
    data = _gql(query)
    for edge in data.get("me", {}).get("projects", {}).get("edges", []):
        p = edge["node"]
        print(f"{GREEN}{p['name']}{RESET}  id={p['id']}")


def deploy(args):
    query = """
    mutation($projectId: String!, $serviceId: String!) {
      serviceInstanceRedeploy(projectId: $projectId, serviceId: $serviceId)
    }
    """
    _gql(query, {"projectId": args.project_id, "serviceId": args.service_id})
    print(f"{GREEN}Redeployment triggered for service {args.service_id}{RESET}")


def list_services(args):
    query = """
    query($projectId: String!) {
      project(id: $projectId) { services { edges { node { id name } } } }
    }
    """
    data = _gql(query, {"projectId": args.project_id})
    for edge in data.get("project", {}).get("services", {}).get("edges", []):
        s = edge["node"]
        print(f"{GREEN}{s['name']}{RESET}  id={s['id']}")


def get_logs(args):
    query = """
    query($deploymentId: String!) {
      deploymentLogs(deploymentId: $deploymentId) { message timestamp }
    }
    """
    data = _gql(query, {"deploymentId": args.deployment_id})
    for log in data.get("deploymentLogs", []):
        print(f"{YELLOW}{log.get('timestamp', '')}{RESET} {log.get('message', '')}")


def set_variable(args):
    query = """
    mutation($projectId: String!, $name: String!, $value: String!) {
      variableUpsert(input: {projectId: $projectId, name: $name, value: $value})
    }
    """
    _gql(query, {
        "projectId": args.project_id,
        "name": args.name,
        "value": args.value,
    })
    print(f"{GREEN}Variable {args.name} set on project {args.project_id}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Railway Project Deployer")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-projects", help="List projects")

    p_deploy = sub.add_parser("deploy", help="Trigger deployment")
    p_deploy.add_argument("--project-id", required=True)
    p_deploy.add_argument("--service-id", required=True)

    p_svc = sub.add_parser("list-services", help="List services")
    p_svc.add_argument("--project-id", required=True)

    p_logs = sub.add_parser("get-logs", help="Get deployment logs")
    p_logs.add_argument("--deployment-id", required=True)

    p_var = sub.add_parser("set-variable", help="Set env variable")
    p_var.add_argument("--project-id", required=True)
    p_var.add_argument("--name", required=True)
    p_var.add_argument("--value", required=True)

    args = parser.parse_args()
    commands = {
        "list-projects": list_projects,
        "deploy": deploy,
        "list-services": list_services,
        "get-logs": get_logs,
        "set-variable": set_variable,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
