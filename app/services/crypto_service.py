# crypto_service.py

from typing import List
from app.ports.coingecko_port import CoingeckoPort
from sqlalchemy.orm import Session
from app.db.models import User
from app.db.base import cache

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


async def get_crypto_list(client: CoingeckoPort) -> List[dict]:
    data = await client.fetch_crypto_list()
    for item in data:
        key = item['symbol']
        cache[key] = {"id": item["id"], "name": item["name"]}
    return cache


async def get_crypto_price(client: CoingeckoPort, crypto_name) -> List[dict]:
    data = await client.fetch_crypto_price(cache[crypto_name]['id'])
    return data


async def add_crypto(
    db: Session,
    client: CoingeckoPort,
    username: str,
) -> List[dict]:
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
