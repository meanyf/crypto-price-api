# crypto.py

from fastapi import APIRouter, Depends
from app.services.crypto_service import get_top_cryptos
from app.adapters.coingecko import CoinGeckoClient
from typing import Annotated
from app.schemas.user import User
from app.api.deps import get_current_user

crypto_router = APIRouter(prefix="/crypto", tags=["crypto"])


async def get_coingecko_client() -> CoinGeckoClient:
    return CoinGeckoClient(timeout=5.0)


@crypto_router.get("/")
async def list_cryptos(current_user: Annotated[User, Depends(get_current_user)], client: CoinGeckoClient = Depends(get_coingecko_client)):
    return await get_top_cryptos(client, per_page=10)
