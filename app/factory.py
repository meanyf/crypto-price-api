# factory.py
from contextlib import asynccontextmanager
from dataclasses import dataclass
from fastapi import FastAPI
import httpx

from app.adapters.coingecko_adapter import CoinGeckoClient, CoinGeckoConfig


@dataclass
class Adapters:
    coingecko: CoinGeckoClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)

    cg_http = httpx.AsyncClient(
        base_url=CoinGeckoClient.BASE, limits=limits, timeout=None
    )

    cg_cfg = CoinGeckoConfig(timeout=5.0)

    coingecko_adapter = CoinGeckoClient(http_client=cg_http, cfg=cg_cfg)

    app.state.coingecko = coingecko_adapter

    try:
        yield
    finally:
        await cg_http.aclose()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    return app
