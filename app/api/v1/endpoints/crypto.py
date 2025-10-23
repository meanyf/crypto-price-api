# crypto.py

from fastapi import APIRouter, Depends
from app.services.crypto_service import get_top_cryptos, get_crypto_list, get_crypto_price
from app.adapters.coingecko_adapter import CoinGeckoAdapter
from typing import Annotated
from app.schemas.user import User
from app.api.deps import get_current_user, get_coingecko_client
crypto_router = APIRouter(prefix="/crypto", tags=["crypto"])

@crypto_router.get("/")
async def list_cryptos(current_user: Annotated[User, Depends(get_current_user)], client: CoinGeckoAdapter = Depends(get_coingecko_client)):
    return await get_top_cryptos(client)


@crypto_router.get("/list")
async def list_cryptos(
    current_user: Annotated[User, Depends(get_current_user)],
    client: CoinGeckoAdapter = Depends(get_coingecko_client),
):
    return await get_crypto_list(client)


@crypto_router.get("/{symbol}")  # GET /crypto/{symbol}
async def crypto_symbol(
    symbol: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: CoinGeckoAdapter = Depends(get_coingecko_client),
):
    return await get_crypto_price(client, symbol)
