# 

## 1. Запуск 
```bash
cp .env.example .env
docker-compose up --build
docker-compose exec app alembic upgrade head 
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 
uvicorn cryptoserver:app --host 0.0.0.0 --port 8000 --reload

```
