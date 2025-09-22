import requests
import pandas as pd
from datetime import datetime
import time

def fetch_kucoin_st_tokens():
    """
    Fetches ST-tagged tokens from KuCoin API without checking response code.
    """
    url = "https://api.kucoin.com/api/v2/symbols"
    time.sleep(0.2)  # be polite to the API
    print("📡 Fetching symbol data from KuCoin API...")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json().get('data', [])

        st_tokens = [
            {
                'pair': symbol.get('symbol'),
                'base': symbol.get('baseCurrency'),
                'quote': symbol.get('quoteCurrency'),
                'st': symbol.get('st'),
                'status': symbol.get('enableTrading'),
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            }
            for symbol in data
            if symbol.get('st') == "true"
        ]

        return st_tokens

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []

# --- Run Script ---
st_tokens = fetch_kucoin_st_tokens()

filename = "ST_KuCoin.csv"

if st_tokens:
    df = pd.DataFrame(st_tokens)
    print(f"\n⚠️ Found {len(st_tokens)} ST-tagged trading pairs:")
    print(df[['pair', 'base', 'quote', 'st']])
else:
    df = pd.DataFrame(columns=['pair', 'base', 'quote', 'st', 'status', 'last_updated'])
    print("\n✅ No trading pairs are currently ST-tagged")

df.to_csv(filename, index=False)
print(f"\n💾 Data saved to {filename}")
