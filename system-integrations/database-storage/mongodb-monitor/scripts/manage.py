#!/usr/bin/env python3
"""
MongoDB Atlas Cluster Monitor - Check connections and slow queries.
Uses MongoDB Atlas Admin API via requests with digest auth.
"""

import sys
import os
import json
import argparse

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://cloud.mongodb.com/api/atlas/v2"


def get_config():
    public_key = os.environ.get("MONGODB_PUBLIC_KEY")
    private_key = os.environ.get("MONGODB_PRIVATE_KEY")
    group_id = os.environ.get("MONGODB_GROUP_ID")
    if not public_key:
        print(f"{RED}Error: MONGODB_PUBLIC_KEY environment variable not set.{RESET}")
        sys.exit(1)
    if not private_key:
        print(f"{RED}Error: MONGODB_PRIVATE_KEY environment variable not set.{RESET}")
        sys.exit(1)
    if not group_id:
        print(f"{RED}Error: MONGODB_GROUP_ID environment variable not set.{RESET}")
        sys.exit(1)
    return public_key, private_key, group_id


def api_request(method, endpoint, public_key, private_key, params=None):
    try:
        import requests
        from requests.auth import HTTPDigestAuth
    except ImportError:
        print(f"{RED}Error: 'requests' library not installed. Run: pip install requests{RESET}")
        sys.exit(1)

    headers = {"Accept": "application/vnd.atlas.2023-01-01+json", "Content-Type": "application/json"}
    url = f"{BASE_URL}{endpoint}"

    resp = requests.request(method, url, headers=headers, auth=HTTPDigestAuth(public_key, private_key),
                            params=params, timeout=30)
    if resp.status_code >= 400:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.text else None


def list_clusters():
    public_key, private_key, group_id = get_config()
    print(f"{YELLOW}Listing clusters...{RESET}")

    data = api_request("GET", f"/groups/{group_id}/clusters", public_key, private_key)
    clusters = data.get("results", [])
    print(f"{GREEN}Found {len(clusters)} clusters:{RESET}")
    for c in clusters:
        state = c.get("stateName", "UNKNOWN")
        color = GREEN if state == "IDLE" else YELLOW
        print(f"  {c['name']} [{color}{state}{RESET}] type={c.get('clusterType', 'N/A')} "
              f"version={c.get('mongoDBVersion', 'N/A')}")


def get_metrics(cluster, metric="CONNECTIONS", period="PT1H", granularity="PT5M"):
    public_key, private_key, group_id = get_config()
    print(f"{YELLOW}Getting {metric} metrics for '{cluster}'...{RESET}")

    # Get process list first
    data = api_request("GET", f"/groups/{group_id}/processes", public_key, private_key)
    processes = [p for p in data.get("results", []) if cluster in p.get("userAlias", "")]
    if not processes:
        print(f"{RED}No processes found for cluster '{cluster}'.{RESET}")
        sys.exit(1)

    proc = processes[0]
    host_id = f"{proc['hostname']}:{proc['port']}"
    params = {"granularity": granularity, "period": period, "m": metric}
    metrics = api_request("GET", f"/groups/{group_id}/processes/{host_id}/measurements",
                          public_key, private_key, params=params)

    measurements = metrics.get("measurements", [])
    print(f"{GREEN}Metrics for {cluster} ({metric}):{RESET}")
    for m in measurements:
        print(f"  {m['name']}:")
        for dp in m.get("dataPoints", [])[-5:]:
            val = dp.get("value", "N/A")
            print(f"    {dp['timestamp']}: {val}")


def slow_queries(cluster, duration=100):
    public_key, private_key, group_id = get_config()
    print(f"{YELLOW}Finding slow queries on '{cluster}' (>{duration}ms)...{RESET}")

    params = {"duration": duration}
    data = api_request("GET", f"/groups/{group_id}/processes/{cluster}/performanceAdvisor/slowQueryLogs",
                       public_key, private_key, params=params)
    queries = data.get("slowQueries", [])
    print(f"{GREEN}Found {len(queries)} slow queries:{RESET}")
    for q in queries[:10]:
        print(f"\n  Namespace: {q.get('namespace', 'N/A')}")
        print(f"  Duration:  {q.get('millis', 'N/A')}ms")
        print(f"  Command:   {json.dumps(q.get('command', {}), default=str)[:120]}")


def list_databases(cluster):
    public_key, private_key, group_id = get_config()
    print(f"{YELLOW}Listing databases for '{cluster}'...{RESET}")

    # Get process
    data = api_request("GET", f"/groups/{group_id}/processes", public_key, private_key)
    processes = [p for p in data.get("results", []) if cluster in p.get("userAlias", "")]
    if not processes:
        print(f"{RED}No processes found for cluster '{cluster}'.{RESET}")
        sys.exit(1)

    proc = processes[0]
    host_id = f"{proc['hostname']}:{proc['port']}"
    dbs = api_request("GET", f"/groups/{group_id}/processes/{host_id}/databases", public_key, private_key)
    results = dbs.get("results", [])
    print(f"{GREEN}Found {len(results)} databases:{RESET}")
    for db in results:
        print(f"  {db.get('databaseName', 'N/A')}  size={db.get('sizeOnDisk', 'N/A')} bytes")


def get_alerts():
    public_key, private_key, group_id = get_config()
    print(f"{YELLOW}Getting alerts...{RESET}")

    data = api_request("GET", f"/groups/{group_id}/alerts", public_key, private_key, params={"status": "OPEN"})
    alerts = data.get("results", [])
    if not alerts:
        print(f"{GREEN}No active alerts.{RESET}")
        return

    print(f"{RED}Found {len(alerts)} active alerts:{RESET}")
    for a in alerts:
        print(f"  [{a.get('status')}] {a.get('eventTypeName', 'N/A')}")
        print(f"    Created: {a.get('created', 'N/A')}")
        print(f"    Cluster: {a.get('clusterName', 'N/A')}")


def main():
    parser = argparse.ArgumentParser(description="MongoDB Atlas Cluster Monitor")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-clusters", help="List all clusters")

    p_metrics = subparsers.add_parser("get-metrics", help="Get cluster metrics")
    p_metrics.add_argument("--cluster", required=True, help="Cluster name")
    p_metrics.add_argument("--metric", default="CONNECTIONS", help="Metric name")
    p_metrics.add_argument("--period", default="PT1H", help="Time period (ISO 8601)")
    p_metrics.add_argument("--granularity", default="PT5M", help="Data granularity")

    p_slow = subparsers.add_parser("slow-queries", help="Find slow queries")
    p_slow.add_argument("--cluster", required=True, help="Cluster name")
    p_slow.add_argument("--duration", type=int, default=100, help="Min duration in ms")

    p_dbs = subparsers.add_parser("list-databases", help="List databases in a cluster")
    p_dbs.add_argument("--cluster", required=True, help="Cluster name")

    subparsers.add_parser("get-alerts", help="Get active alerts")

    args = parser.parse_args()

    if args.command == "list-clusters":
        list_clusters()
    elif args.command == "get-metrics":
        get_metrics(args.cluster, args.metric, args.period, args.granularity)
    elif args.command == "slow-queries":
        slow_queries(args.cluster, args.duration)
    elif args.command == "list-databases":
        list_databases(args.cluster)
    elif args.command == "get-alerts":
        get_alerts()


if __name__ == "__main__":
    main()
