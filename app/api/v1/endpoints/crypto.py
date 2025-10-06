# crypto.py

from fastapi import APIRouter, HTTPException
import httpx
from datetime import datetime

crypto_router = APIRouter(prefix="/crypto", tags=["crypto"])


@crypto_router.get("/")
async def get_cryptos():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": "false",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    if response.status_code != 200:
        raise HTTPException(
            status_code=502, detail="Failed to fetch data from CoinGecko"
        )

    data = response.json()

    # преобразуем под свой формат
    cryptos = [
        {
            "symbol": coin["symbol"].upper(),
            "name": coin["name"],
            "current_price": coin["current_price"],
            "last_updated": coin["last_updated"],
        }
        for coin in data
    ]

    return {"cryptos": cryptos}
