# crypto_service.py

from typing import List
from app.core.ports import CoinGeckoClientPort


async def get_top_cryptos(
    client: CoinGeckoClientPort, per_page: int = 10
) -> List[dict]:
    data = await client.fetch_markets(per_page=per_page)
    return [
        {
            "symbol": coin["symbol"].upper(),
            "name": coin["name"],
            "current_price": coin["current_price"],
            "last_updated": coin["last_updated"],
        }
        for coin in data
    ]
