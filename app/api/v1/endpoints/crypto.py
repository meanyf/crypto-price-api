# crypto.py

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.crypto_service import (
    set_crypto_mapping,
    get_crypto_price,
    add_crypto,
    list_cryptos,
    get_crypto_by_symbol,
    update_crypto_by_symbol,
    list_history,
    get_stats,
    delete_crypto_by_symbol
)
from app.adapters.coingecko_adapter import CoinGeckoAdapter
from typing import Annotated
from app.schemas.user import User
from app.api.deps import get_db
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_coingecko_client
crypto_router = APIRouter(prefix="/crypto", tags=["crypto"])

templates = Jinja2Templates(directory="templates")


@crypto_router.get("/", response_class=HTMLResponse)
async def index(db: Annotated[Session, Depends(get_db)], request: Request):
    cryptos = await list_cryptos(db)
    return templates.TemplateResponse(
        "users/crypto.html", {"request": request, "cryptos": cryptos}
    )


@crypto_router.get("/{symbol}/history")
async def history(
    db: Annotated[Session, Depends(get_db)],
    request: Request,
    symbol: str, 
):
    history = await list_history(db, symbol)
    print(history)
    return templates.TemplateResponse(
        "users/crypto_history.html", {"request": request, "history": history}
    )


@crypto_router.get("/{symbol}/stats")
async def stats(
    db: Annotated[Session, Depends(get_db)],
    request: Request,
    symbol: str,
):
    stats = await get_stats(db, symbol)
    return templates.TemplateResponse(
        "users/crypto_stats.html", {"request": request, "stats": stats}
    )


@crypto_router.get("/{symbol}")
async def crypto_symbol(
    db: Annotated[Session, Depends(get_db)],
    symbol: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await get_crypto_by_symbol(db, symbol)


@crypto_router.delete("/{symbol}") 
async def delete_crypto_symbol(
    db: Annotated[Session, Depends(get_db)],
    symbol: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    await delete_crypto_by_symbol(db, symbol)


@crypto_router.put("/{symbol}/refresh")
async def crypto_symbol_price(
    db: Annotated[Session, Depends(get_db)],
    symbol: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: CoinGeckoAdapter = Depends(get_coingecko_client),
):
    return await update_crypto_by_symbol(db, client, symbol)


@crypto_router.post("/")
async def add_symbol(
    db: Annotated[Session, Depends(get_db)],
    symbol: Annotated[str, Form()],
    current_user: Annotated[User, Depends(get_current_user)],
    client: CoinGeckoAdapter = Depends(get_coingecko_client),
):
    return await add_crypto(db, client, symbol)
