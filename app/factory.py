# factory.py
from contextlib import asynccontextmanager
import contextlib as _contextlib
from dataclasses import dataclass
from fastapi import FastAPI
import httpx
import asyncio
import logging

from app.adapters.coingecko_adapter import CoinGeckoAdapter, CoinGeckoConfig
from app.services.poller import poll_loop

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # создаём HTTP-клиента и адаптер
    coingecko_client = httpx.AsyncClient(base_url=CoinGeckoAdapter.BASE)
    coingecko_cfg = CoinGeckoConfig(timeout=5.0)
    coingecko_adapter = CoinGeckoAdapter(
        http_client=coingecko_client, cfg=coingecko_cfg
    )
    app.state.coingecko = coingecko_adapter

    # событие для управления остановкой poller'a
    app.state._stop_event = asyncio.Event()
    # стартуем цикл опроса
    app.state._poll_task = asyncio.create_task(poll_loop(app, interval=30.0))

    try:
        yield
    finally:
        # сначала закрываем http-клиент
        await coingecko_client.aclose()

        # просим poller завершиться и ждём небольшое время
        app.state._stop_event.set()
        task = app.state._poll_task
        if task:
            try:
                # даём до 10 секунд на аккуратную остановку
                await asyncio.wait_for(task, timeout=10.0)
            except asyncio.TimeoutError:
                logger.warning("Poller didn't finish in time — cancelling")
                task.cancel()
                with _contextlib.suppress(asyncio.CancelledError):
                    await task


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    return app
