# coingecko_port.py

# ports.py

from typing import Protocol, Any, List

DEFAULT_VS_CURRENCY = "usd"


class CoingeckoPort(Protocol):
    async def fetch_markets(
        self,
        vs_currency: str = DEFAULT_VS_CURRENCY,
    ) -> List[dict]: ...
