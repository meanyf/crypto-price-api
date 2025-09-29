# 

## 1. Запуск 
```bash
cp .env.example .env
docker-compose up --build
docker-compose exec app alembic upgrade head
```
