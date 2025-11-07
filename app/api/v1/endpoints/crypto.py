# crypto.py

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.crypto_service import (
    CryptoService,
)
from app.adapters.coingecko_adapter import CoinGeckoAdapter
from typing import Annotated
from app.schemas.user_schema import UserOut
from app.api.deps import get_db
from sqlalchemy.orm import Session
from app.schemas.symbol_schema import Symbol

from app.api.deps import get_current_user, get_coingecko_client, get_crypto_service
crypto_router = APIRouter(prefix="/crypto", tags=["crypto"])

templates = Jinja2Templates(directory="templates")


@crypto_router.get("/")
async def index(
    service: CryptoService = Depends(get_crypto_service),
):
    cryptos = await service.list_cryptos()
    print(cryptos)
    return {'cryptos': cryptos}
    # return templates.TemplateResponse(
    #     "crypto/crypto.html", {"request": request, "cryptos": cryptos}
    # )


@crypto_router.get("/{symbol}/history")
async def history(
    symbol: str,
    service: CryptoService = Depends(get_crypto_service),
):
    history = await service.list_history(symbol)
    return {"symbol": symbol,
            'history': history
            }
    # return templates.TemplateResponse(
    #     "crypto/crypto_history.html", {"request": request, "history": history}
    # )


@crypto_router.get("/{symbol}/stats")
async def stats(
    symbol: str,
    service: CryptoService = Depends(get_crypto_service),
):
    stats = await service.get_stats(symbol.lower())
    return stats
    # return templates.TemplateResponse(
    #     "crypto/crypto_stats.html", {"request": request, "stats": stats}
    # )


@crypto_router.get("/{symbol}")
async def crypto_symbol(
    symbol: str,
    service: CryptoService = Depends(get_crypto_service),
):
    return await service.get_crypto_by_symbol(symbol.lower())


@crypto_router.delete("/{symbol}") 
async def delete_crypto_symbol(
    symbol: str,
    service: CryptoService = Depends(get_crypto_service),
):
    await service.delete_crypto_by_symbol(symbol.lower())
    return {}


@crypto_router.put("/{symbol}/refresh")
async def crypto_symbol_price(
    symbol: str,
    service: CryptoService = Depends(get_crypto_service),
):
    return await service.update_crypto_by_symbol(symbol.lower())


@crypto_router.post("/")
async def add_symbol(
    symbol: Symbol,
    service: CryptoService = Depends(get_crypto_service),
):
    return await service.add_crypto(symbol.symbol.lower())
