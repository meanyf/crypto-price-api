# crypto_service.py

from decimal import Decimal
from typing import List
from app.ports.coingecko_port import CoingeckoPort
from sqlalchemy.orm import Session
from app.db.models import Crypto, PriceHistory, User
from app.db.base import cache
from datetime import datetime, timezone
from app.db.crud import create_crypto, get_cryptos, get_crypto, get_crypto_history

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
    # print(data[:3])
    for item in data:
        key = item['symbol']
        cache[key] = {"id": item["id"], "name": item["name"]}
    # print(dict(islice(cache.items(), 3)))
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


async def list_history(db: Session, symbol: str) -> List[PriceHistory]:
    return get_crypto_history(db, symbol)


async def add_crypto(db: Session,
                     client: CoingeckoPort,
                     crypto_symbol: str) -> Crypto:
    if not cache:
        await set_crypto_mapping(client)

    id = cache[crypto_symbol]["id"]
    data = await client.fetch_crypto_price(id)
    d = {
        "symbol": crypto_symbol,
        "name": cache[crypto_symbol]["name"],
        "current_price": data[id]["usd"],
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }

    crypto = create_crypto(d)   
    crypto.history.append(
        PriceHistory(
            price=Decimal(str(crypto.current_price)),
            timestamp=crypto.last_updated
        )
    )
    db.add(crypto)            

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise
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


async def get_crypto_history_by_symbol(db: Session, crypto_symbol: str) -> List[dict]:
    crypto = get_crypto_history(db, crypto_symbol)
    if crypto is not None:
        return crypto
    else:
        raise CryptNotFound


async def update_crypto_by_symbol(db: Session,
    client: CoingeckoPort,
    crypto_symbol: str):
    crypto = get_crypto(db, crypto_symbol)
    if not cache:
        await set_crypto_mapping(client)

    if crypto is not None: 
        id = cache[crypto_symbol]["id"]
        data = await client.fetch_crypto_price(id)
        crypto.current_price = data[id]['usd']
        crypto.last_updated = datetime.now(timezone.utc).isoformat()
        crypto.history.append(
            PriceHistory(
                price=Decimal(str(crypto.current_price)), timestamp=crypto.last_updated
            )
        )

        try:
            db.commit()   
        except Exception:
            db.rollback()
            raise

        db.refresh(crypto)     
        return crypto
    else:
        raise CryptNotFound
