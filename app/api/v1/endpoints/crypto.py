# crypto.py

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.crypto_service import set_crypto_mapping, get_crypto_price, add_crypto, show_cryptos
from app.adapters.coingecko_adapter import CoinGeckoAdapter
from typing import Annotated
from app.schemas.user import User
from app.api.deps import get_db
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_coingecko_client
crypto_router = APIRouter(prefix="/crypto", tags=["crypto"])

# @crypto_router.get("/")
# async def list_cryptos(current_user: Annotated[User, Depends(get_current_user)], client: CoinGeckoAdapter = Depends(get_coingecko_client)):
#     return await get_top_cryptos(client)


# @crypto_router.get("/list")
# async def list_cryptos(
#     current_user: Annotated[User, Depends(get_current_user)],
#     client: CoinGeckoAdapter = Depends(get_coingecko_client),
# ):
#     return await set_crypto_mapping(client)

templates = Jinja2Templates(directory="templates")


@crypto_router.get("/", response_class=HTMLResponse)
async def index(db: Annotated[Session, Depends(get_db)], request: Request):
    cryptos = await show_cryptos(db)
    return templates.TemplateResponse(
        "users/crypto.html", {"request": request, "cryptos": cryptos}
    )


@crypto_router.get("/{symbol}")  # GET /crypto/{symbol}
async def crypto_symbol(
    symbol: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: CoinGeckoAdapter = Depends(get_coingecko_client),
):
    return await get_crypto_price(client, symbol)


@crypto_router.post("/")
async def add_symbol(
    db: Annotated[Session, Depends(get_db)],
    symbol: Annotated[str, Form()],
    current_user: Annotated[User, Depends(get_current_user)],
    client: CoinGeckoAdapter = Depends(get_coingecko_client),
):
    return await add_crypto(db, client, symbol)
