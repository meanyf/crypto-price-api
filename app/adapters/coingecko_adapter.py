# coingecko_adapter.py
from dataclasses import dataclass
from typing import Any, Dict
import httpx

from app.core.exceptions import ExternalAPIError, ExternalServiceError, ExternalTimeoutError
from app.ports.coingecko_port import (
    CoingeckoPort,
    DEFAULT_VS_CURRENCY
)


@dataclass
class CoinGeckoConfig:
    timeout: float = 5.0


class CoinGeckoAdapter(CoingeckoPort):
    BASE = "https://api.coingecko.com/api/v3"

    def __init__(
        self, http_client: httpx.AsyncClient, cfg: CoinGeckoConfig = CoinGeckoConfig()
    ):
        self.client = http_client
        self.timeout = cfg.timeout

    async def fetch_markets(self, vs_currency: str = DEFAULT_VS_CURRENCY) -> Any:
        path = "/coins/markets"
        params = {
            "vs_currency": vs_currency
        }

        try:
            resp = await self.client.get(path, params=params, timeout=self.timeout)

        except httpx.TimeoutException as e:
            raise ExternalTimeoutError("CoinGecko timeout") from e
        except httpx.RequestError as e:
            raise ExternalServiceError("Failed to request CoinGecko") from e

        if resp.status_code != 200:
            raise ExternalServiceError(f"CoinGecko returned {resp.status_code}", resp.status_code)
        return resp.json()

    async def fetch_crypto_list(self): 
        path = "/coins/list"
        try:
            resp = await self.client.get(path, timeout=self.timeout)
        except httpx.TimeoutException as e:
            raise ExternalTimeoutError("CoinGecko timeout") from e
        if resp.status_code != 200:
            raise ExternalServiceError(
                f"CoinGecko returned {resp.status_code}", resp.status_code
            )
        return resp.json()

    async def fetch_crypto_price(
        self, crypto_name, vs_currency: str = DEFAULT_VS_CURRENCY
    ):
        path = "/simple/price"
        params = {
            "ids": crypto_name,  # ✅ Указываем, какую крипту хотим
            "vs_currencies": vs_currency,
        }
        try:
            resp = await self.client.get(path, params=params, timeout=self.timeout)
            print(resp)
            print(resp.json())
        except httpx.TimeoutException as e:
            raise ExternalTimeoutError("CoinGecko timeout") from e
        if resp.status_code != 200:
            raise ExternalServiceError(
                f"CoinGecko returned {resp.status_code}", resp.status_code
            )
        return resp.json()
