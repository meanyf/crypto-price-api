# poller.py

import asyncio
import logging
import contextlib

from app.services.crypto_service import update_cryptos
from app.db.session import SessionLocal  # <- проверьте путь к вашей сессии

logger = logging.getLogger(__name__)


async def _run_one_iteration(client, interval: float):
    """Создаёт сессию, вызывает update_cryptos и гарантированно закрывает сессию."""
    db = SessionLocal()
    try:
        await update_cryptos(db, client)
    finally:
        try:
            db.close()
        except Exception:
            logger.exception("Ошибка при закрытии DB-сессии")


async def poll_loop(app, interval: float = 30.0):
    """
    Асинхронный бесконечный цикл, который каждые `interval` секунд вызывает update_cryptos.
    Останавливается, когда app.state._stop_event.set() вызывается (в lifespan shutdown).
    """
    client = app.state.coingecko
    stop_event: asyncio.Event = app.state._stop_event

    logger.info("Poller started with interval %.1f sec", interval)

    while not stop_event.is_set():
        try:
            await _run_one_iteration(client, interval)
        except Exception:
            logger.exception("Ошибка в poll_loop при обновлении крипто-данных")

        # Ждём либо timeout, либо событие остановки
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except asyncio.TimeoutError:
            # таймаут, идём на следующую итерацию
            continue

    logger.info("Poller stopped")
