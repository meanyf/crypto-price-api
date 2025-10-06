# coingecko.py

import httpx
from app.core.exceptions import ExternalServiceError, ExternalTimeoutError
from app.core.ports import CoinGeckoClientPort


class CoinGeckoClient(CoinGeckoClientPort):
    BASE = "https://api.coingecko.com/api/v3"

    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout

    async def fetch_markets(self, vs_currency="usd", per_page=10, page=1):
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
        except httpx.ReadTimeout as e:
            raise ExternalTimeoutError("CoinGecko timeout") from e
        except httpx.RequestError as e:
            raise ExternalServiceError("Failed to request CoinGecko") from e

        if resp.status_code != 200:
            raise ExternalServiceError(f"CoinGecko returned {resp.status_code}")
        return resp.json()
