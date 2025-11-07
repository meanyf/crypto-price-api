# app/adapters/redis_async_adapter.py
import json
from typing import Any, Optional, Union
import redis.asyncio as aioredis  # pip install redis>=4
from app.ports.cache_port import CachePort


class RedisCache(CachePort):
    """
    Асинхронный адаптер Redis, реализующий CachePort.
    Использует JSON-сериализацию для значений и префикс для неймспейса.

    Ожидает aioredis.Redis (redis.asyncio.Redis).
    """

    def __init__(self, redis_client: aioredis.Redis, *, key_prefix: str = "app:"):
        self.client = redis_client
        self.prefix = key_prefix

    def key(self, key: str) -> str:
        return f"{self.prefix}{key}"

    async def get(self, key: str) -> Optional[Any]:
        raw = await self.client.get(self.key(key))
        if raw is None:
            return None

        # raw может быть bytes или str в зависимости от decode_responses
        if isinstance(raw, bytes):
            try:
                text = raw.decode("utf-8")
            except Exception:
                # не UTF-8 — возвращаем сырые bytes
                return raw
        else:
            text = raw  # тип str

        # попытаться распарсить как JSON
        try:
            return json.loads(text)
        except (ValueError, TypeError):
            # если не JSON — вернуть строку
            return text

    async def set(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        # сериализуем в JSON и записываем bytes (чтобы не зависеть от decode_responses)
        payload = json.dumps(value, ensure_ascii=False).encode("utf-8")
        if ttl_seconds is None:
            await self.client.set(self.key(key), payload)
        else:
            # setex принимает seconds и value
            await self.client.setex(self.key(key), ttl_seconds, payload)

    async def delete(self, key: str) -> None:
        await self.client.delete(self.key(key))

    async def exists(self, key: str) -> bool:
        # exists возвращает количество существующих ключей (0 или 1)
        res = await self.client.exists(self.key(key))
        return bool(res)

    async def close(self) -> None:
        """
        Аккуратно закрывает клиент и пул соединений.
        Вызывать при завершении приложения.
        """
        try:
            await self.client.close()
        finally:
            # некоторые реализации требуют дисконнекта пула
            pool = getattr(self.client, "connection_pool", None)
            if pool is not None:
                # disconnect() — sync or awaitable depending on implementation; делаем await если поддерживает
                disconnect = getattr(pool, "disconnect", None)
                if callable(disconnect):
                    maybe = disconnect()
                    if hasattr(maybe, "__await__"):
                        await maybe
