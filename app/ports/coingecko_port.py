# coingecko_port.py

# ports.py

from typing import Protocol, Any, List

DEFAULT_VS_CURRENCY = "usd"
DEFAULT_PER_PAGE = 10
DEFAULT_PAGE = 1


class CoingeckoPort(Protocol):
    async def fetch_markets(
        self,
        vs_currency: str = DEFAULT_VS_CURRENCY,
        per_page: int = DEFAULT_PER_PAGE,
        page: int = DEFAULT_PAGE,
    ) -> List[dict]: ...
