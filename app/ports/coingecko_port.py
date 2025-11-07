# coingecko_port.py

# ports.py

from typing import Protocol, Any, List

DEFAULT_VS_CURRENCY = "usd"


class CoingeckoPort(Protocol):
    async def fetch_crypto_list(self) -> dict: ...

    async def fetch_crypto_price(
        self,
        crypto_name,
        vs_currency: str = DEFAULT_VS_CURRENCY,
    ) -> dict: ...
