#!/usr/bin/env python3
"""
Financial Report Summarizer — OC-0164
Parse 10-K/10-Q filings and extract key metrics via SEC EDGAR.
"""

import os
import sys
import json
import argparse
import re
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

EDGAR_BASE   = "https://data.sec.gov"
EDGAR_SEARCH = "https://efts.sec.gov/LATEST/search-index"
OPENAI_URL   = "https://api.openai.com/v1/chat/completions"

HEADERS = {"User-Agent": "FinancialReportSummarizer/1.0 contact@example.com"}


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _get_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        _die("OPENAI_API_KEY is not set.")
    return key


def _ai_summarize(text: str, prompt_prefix: str) -> str:
    truncated = text[:4000]
    resp = requests.post(
        OPENAI_URL,
        headers={
            "Authorization": f"Bearer {_get_api_key()}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a financial analyst expert. Provide clear, structured analysis.",
                },
                {"role": "user", "content": f"{prompt_prefix}\n\nText:\n{truncated}"},
            ],
            "max_tokens": 800,
        },
        timeout=60,
    )
    if not resp.ok:
        _die(f"OpenAI API {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def search_filings(company: str, form_type: str = "10-K", limit: int = 10):
    print(f"{YELLOW}Searching EDGAR for {company} {form_type} filings...{RESET}")
    resp = requests.get(
        "https://efts.sec.gov/LATEST/search-index?q=%22{}%22&dateRange=custom&startdt=2020-01-01&forms={}".format(
            company.replace(" ", "+"), form_type
        ),
        headers=HEADERS,
        timeout=30,
    )

    # Use the full text search endpoint
    resp = requests.get(
        "https://efts.sec.gov/LATEST/search-index",
        params={
            "q": f'"{company}"',
            "forms": form_type,
            "dateRange": "custom",
            "startdt": "2020-01-01",
        },
        headers=HEADERS,
        timeout=30,
    )

    if not resp.ok:
        # Try alternate EDGAR search
        resp = requests.get(
            f"https://www.sec.gov/cgi-bin/browse-edgar",
            params={
                "company": company,
                "CIK": "",
                "type": form_type,
                "dateb": "",
                "owner": "include",
                "count": limit,
                "search_text": "",
                "action": "getcompany",
                "output": "atom",
            },
            headers=HEADERS,
            timeout=30,
        )
        if resp.ok:
            print(f"\n{GREEN}EDGAR URL for {company} {form_type}:{RESET}")
            cik_match = re.search(r"CIK=(\d+)", resp.url)
            print(f"  https://www.sec.gov/cgi-bin/browse-edgar?company={company.replace(' ', '+')}&type={form_type}&action=getcompany")
        return

    data = resp.json()
    hits = data.get("hits", {}).get("hits", [])
    if not hits:
        print(f"{YELLOW}No filings found for '{company}' ({form_type}).{RESET}")
        print(f"  Try: https://www.sec.gov/cgi-bin/browse-edgar?company={company.replace(' ', '+')}&type={form_type}&action=getcompany")
        return

    print(f"\n{GREEN}Found {len(hits)} filing(s):{RESET}\n")
    for hit in hits[:limit]:
        src = hit.get("_source", {})
        name    = src.get("entity_name", "")
        cik     = src.get("file_num", "")
        form    = src.get("form_type", "")
        date    = src.get("period_of_report", "")
        print(f"  {CYAN}{form}{RESET}  {BOLD}{name}{RESET}  {date}")
    print()


def summarize(cik: str, form_type: str = "10-K"):
    print(f"{YELLOW}Fetching {form_type} for CIK {cik}...{RESET}")

    # Get company facts from EDGAR
    resp = requests.get(
        f"{EDGAR_BASE}/submissions/CIK{cik.zfill(10)}.json",
        headers=HEADERS,
        timeout=30,
    )
    if not resp.ok:
        _die(f"EDGAR API {resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    company_name = data.get("name", "Unknown")
    filings = data.get("filings", {}).get("recent", {})

    forms  = filings.get("form", [])
    dates  = filings.get("filingDate", [])
    accs   = filings.get("accessionNumber", [])

    # Find most recent 10-K
    idx = next((i for i, f in enumerate(forms) if f == form_type), None)
    if idx is None:
        _die(f"No {form_type} found for CIK {cik}.")

    accession = accs[idx].replace("-", "")
    date = dates[idx]

    print(f"{YELLOW}Loading {company_name} {form_type} filed {date}...{RESET}")

    # Get the filing index
    url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{accs[idx]}-index.htm"
    print(f"  Filing URL: {url}")

    # Generate summary using company facts
    facts_resp = requests.get(
        f"{EDGAR_BASE}/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json",
        headers=HEADERS,
        timeout=30,
    )

    if facts_resp.ok:
        facts = facts_resp.json()
        us_gaap = facts.get("facts", {}).get("us-gaap", {})
        # Extract key revenue/income data
        revenue_data = us_gaap.get("Revenues", us_gaap.get("RevenueFromContractWithCustomerExcludingAssessedTax", {}))
        net_income   = us_gaap.get("NetIncomeLoss", {})

        summary_text = f"Company: {company_name}\nFiling: {form_type}, {date}\n\n"
        if revenue_data:
            units = revenue_data.get("units", {}).get("USD", [])
            if units:
                recent_rev = sorted(units, key=lambda x: x.get("end", ""), reverse=True)[:3]
                summary_text += "Revenue (recent):\n"
                for r in recent_rev:
                    val = r.get("val", 0)
                    period = r.get("end", "")
                    summary_text += f"  {period}: ${val:,}\n"

        prompt = (
            "Summarize this SEC filing information in 5 bullet points covering: "
            "revenue trend, profitability, key risks, competitive position, and outlook."
        )
        result = _ai_summarize(summary_text, prompt)
        print(f"\n{BOLD}{company_name} {form_type} Summary:{RESET}\n{result}\n")
    else:
        print(f"{YELLOW}Could not fetch detailed facts. Visit the filing directly:{RESET}")
        print(f"  {url}")


def key_metrics(cik: str):
    print(f"{YELLOW}Fetching key metrics for CIK {cik}...{RESET}")

    resp = requests.get(
        f"{EDGAR_BASE}/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json",
        headers=HEADERS,
        timeout=30,
    )
    if not resp.ok:
        _die(f"EDGAR API {resp.status_code}: Could not fetch facts.")

    data = resp.json()
    company = data.get("entityName", "")
    gaap    = data.get("facts", {}).get("us-gaap", {})

    metrics = {
        "Revenue": gaap.get("Revenues") or gaap.get("RevenueFromContractWithCustomerExcludingAssessedTax"),
        "Net Income": gaap.get("NetIncomeLoss"),
        "EPS": gaap.get("EarningsPerShareBasic"),
        "Assets": gaap.get("Assets"),
        "Liabilities": gaap.get("Liabilities"),
        "Operating Cash Flow": gaap.get("NetCashProvidedByUsedInOperatingActivities"),
    }

    print(f"\n{BOLD}Key Financial Metrics — {company}:{RESET}\n")
    for metric_name, metric_data in metrics.items():
        if not metric_data:
            continue
        units_data = metric_data.get("units", {})
        unit_key   = "USD" if "USD" in units_data else list(units_data.keys())[0] if units_data else None
        if not unit_key:
            continue
        entries = sorted(units_data[unit_key], key=lambda x: x.get("end", ""), reverse=True)
        annual  = [e for e in entries if e.get("form", "") in ("10-K", "10-K/A")][:3]

        if annual:
            print(f"  {CYAN}{metric_name}:{RESET}")
            for e in annual:
                val  = e.get("val", 0)
                end  = e.get("end", "")[:7]
                if unit_key == "USD":
                    formatted = f"${val:,}"
                else:
                    formatted = f"{val}"
                print(f"    {end}: {GREEN}{formatted}{RESET}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="financial_report_summarizer.py",
        description="Financial Report Summarizer — OC-0164"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("search-filings", help="Search SEC EDGAR for filings")
    p.add_argument("--company", required=True)
    p.add_argument("--form", default="10-K", choices=["10-K", "10-Q", "8-K"])
    p.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("summarize", help="AI-summarize a filing")
    p.add_argument("--cik", required=True, help="SEC CIK number")
    p.add_argument("--form", default="10-K", choices=["10-K", "10-Q"])

    p = sub.add_parser("key-metrics", help="Extract key financial metrics")
    p.add_argument("--cik", required=True)

    args = parser.parse_args()
    dispatch = {
        "search-filings": lambda: search_filings(args.company, args.form, args.limit),
        "summarize":      lambda: summarize(args.cik, args.form),
        "key-metrics":    lambda: key_metrics(args.cik),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
