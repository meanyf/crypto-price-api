# test_requests_auth_time_better.py
import asyncio
import httpx
import time
from datetime import datetime

URL = "http://127.0.0.1:8000/users/me/items/"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzU4OTU0MTU4fQ.4su9dDmAsF6Mc3QNnXeNREyxz4WQ4v5BBqe6otDNj8E"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
CONCURRENCY = 10000


async def worker(
    i: int, client: httpx.AsyncClient, start_event: asyncio.Event, results: list
):
    # ждем сигнала старта, чтобы все начали почти одновременно
    await start_event.wait()
    t0 = time.perf_counter()
    ts = datetime.now().isoformat(timespec="milliseconds")
    try:
        resp = await client.get(URL, headers=HEADERS)
        elapsed = time.perf_counter() - t0
        results.append((i, resp.status_code, elapsed, ts))
    except Exception as e:
        elapsed = time.perf_counter() - t0
        results.append((i, "ERR", elapsed, f"{ts} {e}"))


async def main():
    # Общий клиент (reuse connections)
    async with httpx.AsyncClient() as client:
        # (опционально) warm up один запрос, чтобы прогреть сервер/пулы/DNS
        try:
            await client.get(URL, headers=HEADERS)
        except Exception:
            pass

        start_event = asyncio.Event()
        results = []

        # создаём таски
        tasks = [
            asyncio.create_task(worker(i, client, start_event, results))
            for i in range(CONCURRENCY)
        ]

        # маленькая пауза, чтобы все таски уже были в ожидании
        await asyncio.sleep(0.1)
        total_start = time.perf_counter()
        start_event.set()  # даём сигнал всем начать одновременно

        await asyncio.gather(*tasks)
        total_elapsed = time.perf_counter() - total_start

    # сортируем по индексу, но можно и по времени
    results.sort(key=lambda x: x[0])
    for i, status, elapsed, ts in results:
        print(f"Запрос {i}: {status}, время: {elapsed:.3f} сек, started_at: {ts}")
    print(
        f"\n⏱ Общее время выполнения (для {CONCURRENCY} параллельных): {total_elapsed:.3f} сек"
    )


if __name__ == "__main__":
    asyncio.run(main())
