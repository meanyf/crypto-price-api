# coingecko_adapter.py

# coingecko.py

import httpx
from app.core.exceptions import ExternalServiceError, ExternalTimeoutError
from app.ports.coingecko_port import (
    CoingeckoPort,
    DEFAULT_VS_CURRENCY,
    DEFAULT_PER_PAGE,
    DEFAULT_PAGE,
)

from dataclasses import dataclass


@dataclass
class CoinGeckoConfig:
    timeout: float = 5.0
    retries: int = 2


class CoinGeckoClient(CoingeckoPort):
    BASE = "https://api.coingecko.com/api/v3"

    def __init__(self, http_config: CoinGeckoConfig):
        self.timeout = http_config.timeout

    async def fetch_markets(self, vs_currency=DEFAULT_VS_CURRENCY, per_page=DEFAULT_PER_PAGE, page=DEFAULT_PAGE):
        url = f"{self.BASE}/coins/markets"
        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": page,
            "sparkline": "false",
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, params=params)
        except httpx.TimeoutException as e:
            raise ExternalTimeoutError("CoinGecko timeout") from e
        except httpx.RequestError as e:
            raise ExternalServiceError("Failed to request CoinGecko") from e

        if resp.status_code != 200:
            raise ExternalServiceError(f"CoinGecko returned {resp.status_code}")
        return resp.json()
