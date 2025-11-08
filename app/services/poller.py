# poller.py

import asyncio
import logging

from app.db.session import SessionLocal
from app.services.crypto_service import CryptoService
from app.api.deps import get_coingecko_client, get_cache_client

logger = logging.getLogger(__name__)


async def _run_one_iteration(app, interval: float) -> None:
    """Создаёт сессию, создаёт сервис с реальными зависимостями и гарантированно закрывает сессию."""
    db = SessionLocal()
    try:
        # Попытка взять заранее созданные клиенты из app.state (рекомендуется создавать их на startup)
        coingecko = getattr(app.state, "coingecko", None)
        if coingecko is None:
            # fallback: попробовать получить через фабрику из deps (если это простая фабрика — вызов сработает)
            try:
                coingecko = get_coingecko_client()
            except Exception:
                logger.exception("Не удалось получить coingecko client из deps")
                coingecko = None

        cache = getattr(app.state, "cache", None)
        if cache is None:
            try:
                cache = get_cache_client()
            except Exception:
                logger.exception("Не удалось получить cache client из deps")
                cache = None

        service = CryptoService(db=db, coingecko=coingecko, cache=cache)
        await service.update_cryptos()
    finally:
        try:
            db.close()
        except Exception:
            logger.exception("Ошибка при закрытии DB-сессии")


async def poll_loop(app, interval: float = 30.0) -> None:
    """
    Асинхронный бесконечный цикл, который каждые `interval` секунд вызывает update_cryptos.
    Останавливается, когда app.state._stop_event.set() вызывается (в lifespan shutdown).

    Важно:
    - Рекомендуется в startup создать и положить в app.state объекты:
        app.state.coingecko_client = get_coingecko_client()
        app.state.cache_client = get_cache_client()
        app.state._stop_event = asyncio.Event()
    - Запускать poll_loop через asyncio.create_task(poll_loop(app, interval)) в event loop приложения.
    """
    stop_event: asyncio.Event = getattr(app.state, "_stop_event", None)
    if stop_event is None:
        # на случай, если _stop_event не был создан — создаём и логируем предупреждение
        stop_event = asyncio.Event()
        app.state._stop_event = stop_event
        logger.warning(
            "app.state._stop_event не найден — создан новый Event (рекомендуется задавать на startup)"
        )

    logger.info("Poller started with interval %.1f sec", interval)

    while not stop_event.is_set():
        try:
            await _run_one_iteration(app, interval)
        except Exception:
            logger.exception("Ошибка в poll_loop при обновлении крипто-данных")

        # Ждём либо timeout, либо событие остановки
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except asyncio.TimeoutError:
            # таймаут, идём на следующую итерацию
            continue

    logger.info("Poller stopped")
