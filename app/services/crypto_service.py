# crypto_service.py

from typing import List
from app.ports.coingecko_port import CoingeckoPort
from sqlalchemy.orm import Session
from app.db.models import User
from app.db.base import cache
from datetime import datetime, timezone
from app.db.crud import create_crypto, get_cryptos, get_crypto
from sqlalchemy.exc import IntegrityError
from app.core.exceptions import CryptNotFound

# async def get_top_cryptos(client: CoingeckoPort) -> List[dict]:
#     data = await client.fetch_markets()
#     return [
#         {
#             "symbol": coin["symbol"].upper(),
#             "name": coin["name"],
#             "current_price": coin["current_price"],
#             "last_updated": coin["last_updated"],
#         }
#         for coin in data
#     ]


async def set_crypto_mapping(client: CoingeckoPort) -> List[dict]:
    from itertools import islice
    data = await client.fetch_crypto_list()
    print(data[:3])
    for item in data:
        key = item['symbol']
        cache[key] = {"id": item["id"], "name": item["name"]}
    print(dict(islice(cache.items(), 3)))
    return cache


async def get_crypto_price(client: CoingeckoPort, crypto_symbol) -> List[dict]:
    if not cache:
        await set_crypto_mapping(client)
    data = await client.fetch_crypto_price(cache[crypto_symbol]['id'])
    return data


async def list_cryptos(
    db: Session,
) -> List[dict]:
    return get_cryptos(db)


async def add_crypto(db: Session,
    client: CoingeckoPort, crypto_symbol: str
) -> List[dict]:
    if not cache:
        await set_crypto_mapping(client)
    d = dict()
    id = cache[crypto_symbol]["id"]
    data = await client.fetch_crypto_price(id)
    d["symbol"] = crypto_symbol
    d["name"] = cache[crypto_symbol]['name']
    d["current_price"] = data[id]["usd"]
    unix_timestamp = data[id]["last_updated_at"]
    date = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    d["last_updated"] = date.isoformat().replace('+00:00', 'Z')

    crypto = create_crypto(db, d)  
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise IntegrityError
    db.refresh(crypto)
    return crypto 

async def list_cryptos(
    db: Session,
) -> List[dict]:
    return get_cryptos(db)


async def get_crypto_by_symbol(
    db: Session,
    crypto_symbol: str
) -> List[dict]:
    crypto = get_crypto(db, crypto_symbol)
    if crypto is not None:
        return crypto 
    else:
        raise CryptNotFound
