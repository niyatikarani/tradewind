#!/usr/bin/env python3
"""
fetch_fx.py — Fetch FX rates from exchangerate-api.com and store in quotation.db.

Usage: python fetch_fx.py [--db quotation.db]
Schedule: Daily at 08:00 via Windows Task Scheduler
"""
import argparse
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("Install requests: pip install requests")


def get_api_key() -> str:
    key = os.environ.get("FX_API_KEY", "")
    if not key:
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("FX_API_KEY="):
                    key = line.split("=", 1)[1].strip()
    if not key:
        sys.exit("ERROR: FX_API_KEY not set.")
    return key


def fetch_rate(api_key: str, currency_code: str) -> float | None:
    if currency_code == "INR":
        return 1.0
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{currency_code}/INR"
    try:
        resp = requests.get(url, timeout=15)
        data = resp.json()
        if data.get("result") == "success":
            return float(data["conversion_rate"])
        print(f"  API error for {currency_code}: {data.get('error-type','unknown')}")
    except Exception as e:
        print(f"  Network error for {currency_code}: {e}")
    return None


def run_fetch(db_path: str) -> None:
    if not Path(db_path).exists():
        sys.exit(f"ERROR: {db_path} not found. Run seed.py first.")

    api_key = get_api_key()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    system_user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
    user_id = system_user["id"] if system_user else 1

    currencies = conn.execute("SELECT id, code FROM currencies WHERE is_active=1 AND code != 'INR'").fetchall()
    if not currencies:
        print("No active currencies found.")
        conn.close()
        return

    print(f"Fetching rates for {len(currencies)} currencies at {datetime.now():%Y-%m-%d %H:%M:%S}")
    fetched = 0
    for cur in currencies:
        rate = fetch_rate(api_key, cur["code"])
        if rate is not None:
            conn.execute(
                "INSERT INTO fx_rates(currency_id, rate_vs_inr, source, entered_by) VALUES(?,?,?,?)",
                (cur["id"], rate, "exchangerate-api.com", user_id),
            )
            conn.commit()
            print(f"  {cur['code']}: 1 {cur['code']} = {rate:.4f} INR")
            fetched += 1
        else:
            print(f"  {cur['code']}: FAILED")

    conn.close()
    print(f"\nDone. Fetched {fetched}/{len(currencies)} rates.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="quotation.db")
    args = parser.parse_args()
    run_fetch(args.db)
