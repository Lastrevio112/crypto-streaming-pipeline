""" This code doesn't run in production, I used it to get the 50 most popular currencies to be used in both data sources """

import requests
import json
import os

response = requests.get("https://api.binance.com/api/v3/ticker/24hr")
tickers = response.json()

# Filter USDT pairs only, sort by quote volume descending
usdt_tickers = [
    t for t in tickers
    if t["symbol"].endswith("USDT")
]

top_50 = sorted(
    usdt_tickers,
    key=lambda x: float(x["quoteVolume"]),
    reverse=True
)[:51]

#symbols = [t["symbol"].lower() + '@trade' for t in top_50]
symbols = [t["symbol"] for t in top_50 if t["symbol"] != "USDCUSDT"] 
print(os.getenv("NUM_PARTITIONS"))