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

# async redis
import redis.asyncio as aioredis
from app.adapters.redis_adapter import (
    RedisCache,
)  # предполагаем, что он поддерживает async client
from app.core.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # HTTP клиент и адаптер
    coingecko_client = httpx.AsyncClient(base_url=CoinGeckoAdapter.BASE)
    coingecko_cfg = CoinGeckoConfig(timeout=5.0)
    coingecko_adapter = CoinGeckoAdapter(
        http_client=coingecko_client, cfg=coingecko_cfg
    )
    app.state.coingecko = coingecko_adapter

    # decode_responses=False — оставляем, если вы хотите байты; поменяйте при необходимости
    redis_client = aioredis.from_url(settings.redis_url, decode_responses=False)
    app.state.cache = RedisCache(redis_client, key_prefix="app:")
    from itertools import islice

    data = await app.state.coingecko.fetch_crypto_list()
    print(data[:5])
    for item in data:
        key = item["symbol"].lower()
        value = {"id": item["id"], "name": item["name"]}

        # Сохраняем в Redis вместо app.state.cache
        await app.state.cache.set(key, value, ttl_seconds=86400)  # TTL 24 часа
    print('cache', app.state.cache)
    # событие для управления остановкой poller'a
    app.state._stop_event = asyncio.Event()
    # стартуем цикл опроса (после того, как cache/redis и другие ресурсы готовы)
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
                await asyncio.wait_for(task, timeout=10.0)
            except asyncio.TimeoutError:
                logger.warning("Poller didn't finish in time — cancelling")
                task.cancel()
                with _contextlib.suppress(asyncio.CancelledError):
                    await task

        # закрываем redis-клиент (async)
        try:
            await redis_client.close()
            # дополнительно отсоединяем connection_pool
            if getattr(redis_client, "connection_pool", None):
                await redis_client.connection_pool.disconnect()
        except Exception as e:
            logger.exception("Error closing redis client: %s", e)


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    return app
