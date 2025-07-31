# Gate.io ST-tag Tracker with Daily Append
import requests
import csv
import os
from datetime import datetime

base_url = "https://api.gateio.ws/api/v4"

# Today's date
today_str = datetime.today().strftime('%Y-%m-%d')

# CSV filename
filename = "ST_Gateio.csv"

# Load existing entries (to avoid duplicates)
existing_entries = set()
if os.path.exists(filename):
    with open(filename, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            key = (row['pair'], row['date'])
            existing_entries.add(key)

# Step 1: Get all currency pairs
pairs_resp = requests.get(f"{base_url}/spot/currency_pairs")
pairs = pairs_resp.json()

new_entries = []

# Step 2: Loop and fetch ST-tagged pairs
for pair in pairs:
    pair_name = pair['id']
    url = f"{base_url}/spot/currency_pairs/{pair_name}"
    try:
        resp = requests.get(url)
        if resp.status_code != 200:
            continue
        details = resp.json()
        if details.get("st_tag", False):
            entry_key = (pair_name, today_str)
            if entry_key not in existing_entries:
                new_entries.append({
                    "pair": pair_name,
                    "base": details.get("base"),
                    "quote": details.get("quote"),
                    "st_tag": details.get("st_tag"),
                    "date": today_str
                })
    except Exception as e:
        print(f"Error on {pair_name}: {e}")

# Step 3: Append new data to CSV
write_header = not os.path.exists(filename)

with open(filename, mode="a", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["pair", "base", "quote", "st_tag", "date"])
    if write_header:
        writer.writeheader()
    writer.writerows(new_entries)

print(f"Added {len(new_entries)} new ST-tagged entries for {today_str} to {filename}")
