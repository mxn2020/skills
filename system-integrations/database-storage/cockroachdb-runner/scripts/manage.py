#!/usr/bin/env python3
"""
CockroachDB Query Runner - Execute distributed SQL queries.
Uses psycopg2 for PostgreSQL-compatible connections.
"""

import sys
import os
import json
import argparse

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def get_connection():
    conn_url = os.environ.get("COCKROACH_URL")
    if not conn_url:
        print(f"{RED}Error: COCKROACH_URL environment variable not set.{RESET}")
        sys.exit(1)

    try:
        import psycopg2
    except ImportError:
        print(f"{RED}Error: 'psycopg2' not installed. Run: pip install psycopg2-binary{RESET}")
        sys.exit(1)

    try:
        conn = psycopg2.connect(conn_url)
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f"{RED}Connection error: {e}{RESET}")
        sys.exit(1)


def run_query(sql):
    print(f"{YELLOW}Running query...{RESET}")
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(sql)
        if cur.description:
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            print(f"{GREEN}Returned {len(rows)} rows:{RESET}")
            print(f"  {' | '.join(columns)}")
            print(f"  {'-' * (len(' | '.join(columns)))}")
            for row in rows:
                print(f"  {' | '.join(str(v) for v in row)}")
        else:
            print(f"{GREEN}Query executed (no result set).{RESET}")
    except Exception as e:
        print(f"{RED}Query error: {e}{RESET}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()


def list_databases():
    print(f"{YELLOW}Listing databases...{RESET}")
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SHOW DATABASES")
        rows = cur.fetchall()
        print(f"{GREEN}Found {len(rows)} databases:{RESET}")
        for row in rows:
            print(f"  {row[0]}")
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()


def list_tables(database="defaultdb"):
    print(f"{YELLOW}Listing tables in '{database}'...{RESET}")
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(f"SHOW TABLES FROM {database}")
        rows = cur.fetchall()
        print(f"{GREEN}Found {len(rows)} tables:{RESET}")
        for row in rows:
            # SHOW TABLES returns (schema, table_name, type, ...)
            name = row[1] if len(row) > 1 else row[0]
            print(f"  {name}")
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()


def describe(table):
    print(f"{YELLOW}Describing '{table}'...{RESET}")
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(f"SHOW COLUMNS FROM {table}")
        rows = cur.fetchall()
        print(f"{GREEN}Columns in '{table}':{RESET}")
        for row in rows:
            name = row[0]
            dtype = row[1] if len(row) > 1 else "N/A"
            nullable = "NULL" if (len(row) > 2 and row[2]) else "NOT NULL"
            print(f"  {name}  {dtype}  {nullable}")
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()


def execute(sql):
    print(f"{YELLOW}Executing statement...{RESET}")
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(sql)
        affected = cur.rowcount
        print(f"{GREEN}Statement executed. Rows affected: {affected}{RESET}")
    except Exception as e:
        print(f"{RED}Execution error: {e}{RESET}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="CockroachDB Query Runner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_query = subparsers.add_parser("query", help="Run a SELECT query")
    p_query.add_argument("--sql", required=True, help="SQL query")

    subparsers.add_parser("list-databases", help="List databases")

    p_tables = subparsers.add_parser("list-tables", help="List tables")
    p_tables.add_argument("--database", default="defaultdb", help="Database name")

    p_desc = subparsers.add_parser("describe", help="Describe a table")
    p_desc.add_argument("--table", required=True, help="Table name")

    p_exec = subparsers.add_parser("execute", help="Execute a statement")
    p_exec.add_argument("--sql", required=True, help="SQL statement")

    args = parser.parse_args()

    if args.command == "query":
        run_query(args.sql)
    elif args.command == "list-databases":
        list_databases()
    elif args.command == "list-tables":
        list_tables(args.database)
    elif args.command == "describe":
        describe(args.table)
    elif args.command == "execute":
        execute(args.sql)


if __name__ == "__main__":
    main()
