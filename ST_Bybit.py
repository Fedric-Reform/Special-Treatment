#Bybit ST-tag Tracker with daily append
import requests
import csv
import os
import time
from datetime import datetime

API_URL = "https://api.bybit.com/v5/market/instruments-info"
CSV_FILE = "ST_Bybit.csv"
RATE_LIMIT_DELAY = 0.1  # small delay to respect Bybit rate limits

def fetch_spot_instruments():
    """
    Fetch all spot instruments from Bybit with pagination.
    """
    instruments = []
    params = {"category": "spot"}
    while True:
        resp = requests.get(API_URL, params=params, timeout=30)
        resp.raise_for_status()
        result = resp.json().get("result", {})
        instruments.extend(result.get("list", []))
        cursor = result.get("nextPageCursor")
        if not cursor:
            break
        params["cursor"] = cursor
        time.sleep(RATE_LIMIT_DELAY)
    return instruments

def filter_st_tokens(instruments):
    """
    Return instruments where 'stTag' is '1'.
    """
    return [inst for inst in instruments if inst.get("stTag") == "1"]

def read_existing_for_today():
    """
    Read existing ST tokens from CSV for today's date.
    Returns a set of pairs already logged today.
    """
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    existing_pairs = set()

    if os.path.isfile(CSV_FILE):
        with open(CSV_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["date"].startswith(today_str):
                    existing_pairs.add(row["pair"])
    return existing_pairs

def append_to_csv(st_items):
    """
    Append today's ST-tagged tokens to the CSV file, avoiding duplicates for today.
    """
    file_exists = os.path.isfile(CSV_FILE)
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    existing_today = read_existing_for_today()

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["pair", "base", "quote", "date"])

        for item in st_items:
            base = item.get("baseCoin", "")
            quote = item.get("quoteCoin", "")
            pair = f"{base}/{quote}"
            if pair not in existing_today:
                writer.writerow([pair, base, quote, timestamp])
                print(f"✅ Added new pair for today: {pair}")
            else:
                print(f"⏩ Skipped (already logged today): {pair}")

def main():
    print("Fetching spot instruments from Bybit...")
    instruments = fetch_spot_instruments()
    print(f"Total instruments fetched: {len(instruments)}")

    st_items = filter_st_tokens(instruments)
    if st_items:
        print(f"Found {len(st_items)} ST-tagged instruments.")
        append_to_csv(st_items)
    else:
        print("No ST-tagged instruments found today.")

if __name__ == "__main__":
    main()
