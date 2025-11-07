# crypto_service.py

from decimal import Decimal
from typing import List
from app.ports.cache_port import CachePort
from app.ports.coingecko_port import CoingeckoPort
from sqlalchemy.orm import Session
from app.db.models import Crypto, PriceHistory, User
from datetime import datetime, timezone
from app.db.crud import create_crypto, get_cryptos, get_crypto, get_crypto_history
from app.schemas.crypto_schema import CryptoResponse, PriceHistoryResponse
from sqlalchemy.exc import IntegrityError
from app.core.exceptions import CryptoNotFound, CrptoAlreadyExists


class CryptoService:
    def __init__(
        self, db: Session, coingecko: CoingeckoPort, cache: CachePort | None = None
    ):
        self.db = db
        self.coingecko = coingecko
        self.cache = cache


    async def get_crypto_price(self, crypto_symbol) -> List[dict]:
        data = await self.coingecko.fetch_crypto_price(self.cache.get(crypto_symbol.lower())['id'])
        return data

    async def list_cryptos(self) -> List[dict]:
        db_cryptos = get_cryptos(self.db)
        return [CryptoResponse.model_validate(crypto) for crypto in db_cryptos]

    async def list_history(self, symbol: str) -> List[PriceHistory]:
        db_prices = get_crypto_history(self.db, symbol)
        return [PriceHistoryResponse.model_validate(crypto) for crypto in db_prices]

    async def add_crypto(self, crypto_symbol: str) -> Crypto:
        if not self.cache:
            await self.set_crypto_mapping()

        id = self.cache[crypto_symbol.lower()]["id"]
        data = await self.coingecko.fetch_crypto_price(id)
        d = {
            "symbol": crypto_symbol,
            "name": self.cache[crypto_symbol.lower()]["name"],
            "current_price": data[id]["usd"],
            "last_updated": datetime.now(timezone.utc),
        }
        if get_crypto(self.db, crypto_symbol) is not None:
            raise CrptoAlreadyExists
        crypto = create_crypto(d)   
        crypto.history.append(
            PriceHistory(
                price=Decimal(str(crypto.current_price)),
                timestamp=crypto.last_updated
            )
        )
        if len(crypto.history) > 100:
            crypto.history[:] = sorted(crypto.history, key=lambda h: h.timestamp)[-100:]

        self.db.add(crypto)            

        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            raise
        self.db.refresh(crypto)
        return {'crypto': d}

    async def get_crypto_by_symbol(self, crypto_symbol: str) -> List[dict]:
        crypto = get_crypto(self.db, crypto_symbol)
        if crypto is not None:
            return CryptoResponse.model_validate(crypto) 
        else:
            raise CryptoNotFound

    async def delete_crypto_by_symbol(self, crypto_symbol: str) -> List[dict]:
        crypto = get_crypto(self.db, crypto_symbol)
        if not crypto:
            raise CryptoNotFound
        try:
            self.db.delete(crypto)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    async def get_crypto_history_by_symbol(self, crypto_symbol: str) -> List[dict]:
        crypto = get_crypto_history(self.db, crypto_symbol)
        if crypto is not None:
            return crypto
        else:
            raise CryptoNotFound

    async def update_crypto_by_symbol(self, crypto_symbol: str):
        crypto = get_crypto(self.db, crypto_symbol)
        if not self.cache:
            await self.set_crypto_mapping()
        if crypto is not None:
            id = self.cache[crypto_symbol.lower()]["id"]
            data = await self.coingecko.fetch_crypto_price(id)
            crypto.current_price = data[id]["usd"]
            crypto.last_updated = datetime.now(timezone.utc)
            crypto.history.append(
                PriceHistory(
                    price=Decimal(str(crypto.current_price)), timestamp=crypto.last_updated
                )
            )
            if len(crypto.history) > 100:
                crypto.history[:] = sorted(crypto.history, key=lambda h: h.timestamp)[-100:]
            try:
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            self.db.refresh(crypto)
            return {'crypto': CryptoResponse.model_validate(crypto)}
        else:
            raise CryptoNotFound

    async def update_cryptos(self):
        cryptos = get_cryptos(self.db)
        if not self.cache:
            await self.set_crypto_mapping()
        ids = [self.cache[crypto.symbol]["id"] for crypto in cryptos]
        data = await self.coingecko.fetch_crypto_price(",".join(ids))
        for crypto in cryptos:
            id = self.cache[crypto.symbol]["id"]
            crypto.current_price = data[id]["usd"]
            crypto.last_updated = datetime.now(timezone.utc)
            crypto.history.append(
                PriceHistory(
                    price=Decimal(str(crypto.current_price)), timestamp=crypto.last_updated
                )
            )
            if len(crypto.history) > 100:
                crypto.history[:] = sorted(crypto.history, key=lambda h: h.timestamp)[-100:]
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        for c in cryptos:
            self.db.refresh(c)

    async def get_stats(self, crypto_symbol: str):
        crypto = get_crypto(self.db, crypto_symbol)
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
