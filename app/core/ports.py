# ports.py

from typing import Protocol, Any, List


class CoinGeckoClientPort(Protocol):
    async def fetch_markets(
        self, vs_currency: str = "usd", per_page: int = 10, page: int = 1
    ) -> List[dict]: ...
