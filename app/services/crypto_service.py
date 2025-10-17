# crypto_service.py

from typing import List
from app.ports.coingecko_port import CoingeckoPort


async def get_top_cryptos(client: CoingeckoPort) -> List[dict]:
    data = await client.fetch_markets()
    return [
        {
            "symbol": coin["symbol"].upper(),
            "name": coin["name"],
            "current_price": coin["current_price"],
            "last_updated": coin["last_updated"],
        }
        for coin in data
    ]
