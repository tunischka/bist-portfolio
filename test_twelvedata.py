import os
from twelvedata import TDClient

# API key
api_key = "ca8eff97dc534ee790022de7facc130a"
td = TDClient(apikey=api_key)

# Test farklı formatlar
formats = [
    "THYAO.IS",      # yfinance formatı
    "THYAO",         # Sadece ticker
    "THYAO/XIST",    # ticker/exchange
    "THYAO.XIST",    # ticker.exchange
]

print("Testing BIST symbol formats with Twelve Data API:\n")

for symbol in formats:
    try:
        print(f"Trying: {symbol}")
        ts = td.time_series(
            symbol=symbol,
            interval="1day",
            outputsize=1,
            timezone="Europe/Istanbul"
        )
        data = ts.as_json()
        if data and len(data) > 0:
            print(f"  ✅ SUCCESS! Price: {data[0]['close']}")
            print(f"  Data: {data[0]}\n")
        else:
            print(f"  ❌ No data returned\n")
    except Exception as e:
        print(f"  ❌ Error: {str(e)}\n")

print("\n" + "="*50)
print("Testing with quote endpoint:")
for symbol in formats:
    try:
        print(f"Trying: {symbol}")
        quote = td.quote(symbol=symbol).as_json()
        print(f"  ✅ SUCCESS! {quote}\n")
    except Exception as e:
        print(f"  ❌ Error: {str(e)}\n")
