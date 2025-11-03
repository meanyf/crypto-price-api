# crypto_service.py

from decimal import Decimal
from typing import List
from app.ports.coingecko_port import CoingeckoPort
from sqlalchemy.orm import Session
from app.db.models import Crypto, PriceHistory, User
from app.db.base import cache
from datetime import datetime, timezone
from app.db.crud import create_crypto, get_cryptos, get_crypto, get_crypto_history
from app.schemas.crypto_schema import CryptoResponse, PriceHistoryResponse
from sqlalchemy.exc import IntegrityError
from app.core.exceptions import CryptoNotFound, CrptoAlreadyExists


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


async def list_cryptos(db: Session) -> List[dict]:
    db_cryptos = get_cryptos(db)
    return [CryptoResponse.model_validate(crypto) for crypto in db_cryptos]


async def list_history(db: Session, symbol: str) -> List[PriceHistory]:
    db_prices = get_crypto_history(db, symbol)
    return [PriceHistoryResponse.model_validate(crypto) for crypto in db_prices]


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
        "last_updated": datetime.now(timezone.utc),
    }
    if get_crypto(db, crypto_symbol) is not None:
        raise CrptoAlreadyExists
    crypto = create_crypto(d)   
    crypto.history.append(
        PriceHistory(
            price=Decimal(str(crypto.current_price)),
            timestamp=crypto.last_updated
        )
    )
    if len(crypto.history) > 100:
        # гарантируем сортировку по timestamp, а затем оставляем последние 100
        crypto.history[:] = sorted(crypto.history, key=lambda h: h.timestamp)[-100:]

    db.add(crypto)            

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise
    db.refresh(crypto)
    return {'crypto': d}


async def get_crypto_by_symbol(
    db: Session,
    crypto_symbol: str
) -> List[dict]:
    crypto = get_crypto(db, crypto_symbol)
    if crypto is not None:
        return CryptoResponse.model_validate(crypto) 
    else:
        raise CryptoNotFound


async def delete_crypto_by_symbol(db: Session, crypto_symbol: str) -> List[dict]:
    crypto = get_crypto(db, crypto_symbol)
    if not crypto:
        raise CryptoNotFound
    
    try:
        db.delete(crypto)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e


async def get_crypto_history_by_symbol(db: Session, crypto_symbol: str) -> List[dict]:
    crypto = get_crypto_history(db, crypto_symbol)
    if crypto is not None:
        return crypto
    else:
        raise CryptoNotFound

async def update_crypto_by_symbol(
    db: Session, client: CoingeckoPort, crypto_symbol: str
):

    crypto = get_crypto(db, crypto_symbol)
    if not cache:
        await set_crypto_mapping(client)

    if crypto is not None:
        id = cache[crypto_symbol]["id"]
        data = await client.fetch_crypto_price(id)
        crypto.current_price = data[id]["usd"]
        crypto.last_updated = datetime.now(timezone.utc)
        crypto.history.append(
            PriceHistory(
                price=Decimal(str(crypto.current_price)), timestamp=crypto.last_updated
            )
        )
        if len(crypto.history) > 100:
            # гарантируем сортировку по timestamp, а затем оставляем последние 100
            crypto.history[:] = sorted(crypto.history, key=lambda h: h.timestamp)[-100:]

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(crypto)
        return {'crypto': CryptoResponse.model_validate(crypto)}
    else:
        raise CryptoNotFound


async def update_cryptos(db: Session, client: CoingeckoPort):

    cryptos = get_cryptos(db)
    if not cache:
        await set_crypto_mapping(client)

    ids = [cache[crypto.symbol]["id"] for crypto in cryptos]
    data = await client.fetch_crypto_price(",".join(ids))
    for crypto in cryptos:
        id = cache[crypto.symbol]["id"]
        crypto.current_price = data[id]["usd"]
        crypto.last_updated = datetime.now(timezone.utc)
        crypto.history.append(
            PriceHistory(
                price=Decimal(str(crypto.current_price)), timestamp=crypto.last_updated
            )
        )
        if len(crypto.history) > 100:
            # гарантируем сортировку по timestamp, а затем оставляем последние 100
            crypto.history[:] = sorted(crypto.history, key=lambda h: h.timestamp)[-100:]

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    for c in cryptos:
        db.refresh(c)

async def get_stats(db: Session, crypto_symbol: str):

    crypto = get_crypto(db, crypto_symbol)
    prices =  [h.price for h in crypto.history]
    min_price = min(prices)
    max_price = max(prices)
    avg_price = sum(prices) / len(prices)
    records_count = len(prices)
    current_price = crypto.current_price
    first_price = prices[0]
    price_change = current_price - first_price
    price_change_percent = (price_change / first_price * 100) if first_price else 0.0

    return {
        "symbol": crypto.symbol,
        "current_price": crypto.current_price,
        "stats": {
            "min_price": min_price,
            "max_price": max_price,
            "avg_price": avg_price,
            "price_change": round(price_change, 2),
            "price_change_percent": round(price_change_percent, 4),
            "records_count": records_count,
        },
    }
