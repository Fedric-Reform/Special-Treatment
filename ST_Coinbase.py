import requests
import pandas as pd
from datetime import datetime
import time

def fetch_coinbase_disabled_tokens():
    """
    Fetches Coinbase products that are in 'disabled' status.
    """
    # Coinbase Exchange API endpoint
    url = "https://api.exchange.coinbase.com/products"
    
    # Headers to mimic a legitimate request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }
    
    print("📡 Fetching product data from Coinbase API...")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        products = response.json()
        
        print(f"✅ Successfully fetched {len(products)} trading products")
        
        # Filter for products with 'disabled' status
        disabled_tokens = []
        for product in products:
            status = product.get('status', '').lower()
            # Only include tokens with 'disabled' status
            if status == 'disabled':
                disabled_tokens.append({
                    'pair': product.get('id'),
                    'base': product.get('base_currency'),
                    'quote': product.get('quote_currency'),
                    'status': status,
                    'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return disabled_tokens
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []

# Fetch disabled tokens
disabled_tokens = fetch_coinbase_disabled_tokens()

if disabled_tokens:
    # Create DataFrame
    df = pd.DataFrame(disabled_tokens)
    
    print(f"\n⚠️ Found {len(disabled_tokens)} products with disabled status:")
    print(df[['pair', 'base', 'quote']])
    
    # Save to CSV with timestamp
    filename = f"ST_Coinbase.csv"
    df.to_csv(filename, index=False)
    print(f"\n💾 Data saved to {filename}")
else:
    print("\n✅ No Coinbase trading products are currently disabled")
    # Create empty CSV with headers
    df = pd.DataFrame(columns=['pair', 'base', 'quote', 'status', 'last_updated'])
    filename = f"ST_Coinbase.csv"
    df.to_csv(filename, index=False)
    print(f"📁 Empty file created: {filename}")

# Optional: Print sample if tokens found
if disabled_tokens:
    print("\nSample of disabled tokens:")
    print(df.head(3).to_string(index=False))
