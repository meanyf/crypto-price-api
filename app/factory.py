# factory.py
from contextlib import asynccontextmanager
from dataclasses import dataclass
from fastapi import FastAPI
import httpx

from app.adapters.coingecko_adapter import CoinGeckoAdapter, CoinGeckoConfig


@asynccontextmanager
async def lifespan(app: FastAPI):
    coingecko_client = httpx.AsyncClient(
        base_url=CoinGeckoAdapter.BASE
    )

    coingecko_cfg = CoinGeckoConfig(timeout=5.0)

    coingecko_adapter = CoinGeckoAdapter(http_client=coingecko_client, cfg=coingecko_cfg)

    app.state.coingecko = coingecko_adapter

    try:
        yield
    finally:
        await coingecko_client.aclose()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    return app
