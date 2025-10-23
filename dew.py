# dew.py

import requests

url = "https://api.coingecko.com/api/v3/simple/price"
vs_currency = "usd"

response = requests.get(
    url,
    params={
        'ids': 'bitcoin',
        "vs_currencies": vs_currency,
    },
)

print(response.json())
