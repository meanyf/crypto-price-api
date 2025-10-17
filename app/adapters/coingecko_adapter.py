# coingecko_adapter.py
from dataclasses import dataclass
from typing import Any, Dict
import httpx

from app.core.exceptions import ExternalServiceError, ExternalTimeoutError
from app.ports.coingecko_port import (
    CoingeckoPort,
    DEFAULT_VS_CURRENCY,
    DEFAULT_PER_PAGE,
    DEFAULT_PAGE,
)


@dataclass
class CoinGeckoConfig:
    timeout: float = 5.0


class CoinGeckoClient(CoingeckoPort):
    BASE = "https://api.coingecko.com/api/v3"

    def __init__(
        self, http_client: httpx.AsyncClient, cfg: CoinGeckoConfig = CoinGeckoConfig()
    ):
        # http_client создаётся/закрывается вне адаптера (в factory)
        self.client = http_client
        self.timeout = cfg.timeout

    async def fetch_markets(
        self,
        vs_currency: str = DEFAULT_VS_CURRENCY,
        per_page: int = DEFAULT_PER_PAGE,
        page: int = DEFAULT_PAGE,
    ) -> Any:
        path = "/coins/markets"
        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": page,
            "sparkline": "false",
        }
        try:
            # пер-запросный timeout — адаптер контролирует таймаут
            resp = await self.client.get(path, params=params, timeout=self.timeout)
        except httpx.TimeoutException as e:
            raise ExternalTimeoutError("CoinGecko timeout") from e
        except httpx.RequestError as e:
            raise ExternalServiceError("Failed to request CoinGecko") from e

        if resp.status_code != 200:
            raise ExternalServiceError(f"CoinGecko returned {resp.status_code}")
        return resp.json()
