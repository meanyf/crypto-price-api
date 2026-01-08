# Сервер для хранения цен криптовалют

HTTP REST API сервер для хранения и получения цен криптовалют с системой аутентификации.

## API

### Аутентификация
- **POST /auth/register** - регистрация нового пользователя
  - Body: `{"username": "string", "password": "string"}`
  - Success (201): `{"token": "string"}`
  - Error (400/409): `{"error": "string"}`

- **POST /auth/login** - вход пользователя
  - Body: `{"username": "string", "password": "string"}`
  - Success (200): `{"token": "string"}`
  - Error (400/401): `{"error": "string"}`

### CRUD операции для криптовалют
Все операции требуют аутентификации через заголовок `Authorization: Bearer <token>`

- **GET /crypto** - получить список всех криптовалют
  - Response: `{"cryptos": [{"symbol": "BTC", "name": "Bitcoin", "current_price": 45000.50, "last_updated": "2024-01-01T12:00:00Z"}]}`

- **POST /crypto** - добавить новую криптовалюту для отслеживания
  - Body: `{"symbol": "BTC"}`
  - Success (201): `{"crypto": {...}}`
  - Error (400/409/500): `{"error": "string"}`

- **GET /crypto/{symbol}** - получить информацию о конкретной криптовалюте
  - Success (200): `{"symbol": "BTC", "name": "Bitcoin", "current_price": 45000.50, "last_updated": "2024-01-01T12:00:00Z"}`
  - Error (404): `{"error": "string"}`

- **PUT /crypto/{symbol}/refresh** - принудительно обновить цену криптовалюты
  - Success (200): `{"crypto": {...}}`
  - Error (404/500): `{"error": "string"}`

- **GET /crypto/{symbol}/history** - получить историю цен криптовалюты
  - Response: `{"symbol": "BTC", "history": [{"price": 45000.50, "timestamp": "2024-01-01T12:00:00Z"}]}`

- **GET /crypto/{symbol}/stats** - получить статистику по ценам криптовалюты
  - Response: `{"symbol": "BTC", "current_price": 45000.50, "stats": {"min_price": 44000, "max_price": 46000, "avg_price": 45000, "price_change": 1000, "price_change_percent": 2.27, "records_count": 100}}`

- **DELETE /crypto/{symbol}** - удалить криптовалюту из отслеживания (включая историю)
  - Success (200): `{}` (пустой объект)
  - Error (404): `{"error": "string"}`

## Детали реализации

- Все данные хранятся в PostgreSQL
- Каждая криптовалюта хранит историю из максимум 100 последних цен
- Цены обновляются каждые 30 секунд в фоновом потоке
- Пароли хешированы (bcrypt)
- Используются JWT токены для аунтефикации

### CoinGecko API

Для получения всей информации по криптовалютам (включая цены) используется [CoinGecko API](https://docs.coingecko.com/reference/introduction):

CoinGecko использует уникальные ID вместо символов для идентификации криптовалют:
- Symbol: `BTC` → ID: `bitcoin`
- Symbol: `ETH` → ID: `ethereum`
- Symbol: `DOGE` → ID: `dogecoin`

На сервер криптовалюта при добавлении будет приходить в виде тикера (Symbol в маппинге), поэтому этот маппинг запрашивается и кешируется в Redis.


## Структура
```
JWT
├──alembic
│   ├──versions
│   │   ├──123456789abc_create_users.py
│   │   ├──1ec1f5b105d0_create_cryptos_table.py
│   │   └──bb657e669199_create_price_history_table.py
│   ├──env.py
│   ├──README
│   └──script.py.mako
├──app
│   ├──adapters
│   │   ├──__init__.py
│   │   ├──coingecko_adapter.py
│   │   └──redis_adapter.py
│   ├──api
│   │   ├──v1
│   │   │   ├──endpoints
│   │   │   │   ├──__init__.py
│   │   │   │   ├──auth.py
│   │   │   │   └──crypto.py
│   │   │   ├──__init__.py
│   │   │   ├──api.py
│   │   │   └──errors.py
│   │   ├──__init__.py
│   │   └──deps.py
│   ├──core
│   │   ├──__init__.py
│   │   ├──config.py
│   │   ├──exceptions.py
│   │   └──security.py
│   ├──db
│   │   ├──__init__.py
│   │   ├──base.py
│   │   ├──crud.py
│   │   ├──models.py
│   │   └──session.py
│   ├──ports
│   │   ├──__init__.py
│   │   ├──cache_port.py
│   │   └──coingecko_port.py
│   ├──schemas
│   │   ├──__init__.py
│   │   ├──creds_schema.py
│   │   ├──crypto_schema.py
│   │   ├──symbol_schema.py
│   │   ├──token_schema.py
│   │   └──user_schema.py
│   ├──services
│   │   ├──auth_service.py
│   │   ├──crypto_service.py
│   │   └──poller.py
│   ├──__init__.py
│   ├──factory.py
│   └──main.py
├──k8s
│   ├──migrations
│   │   └──app-migrations.yaml
│   ├──app-cm0-configmap.yaml
│   ├──app-cm1-configmap.yaml
│   ├──app-cm2-configmap.yaml
│   ├──app-deployment.yaml
│   ├──app-service.yaml
│   ├──db-service.yaml
│   ├──db-statefulset.yaml
│   ├──Dockerfile
│   ├──env-configmap.yaml
│   ├──postgres-data-persistentvolumeclaim.yaml
│   ├──redis-data-persistentvolumeclaim.yaml
│   ├──redis-service.yaml
│   └──redis-statefulset.yaml
├──templates
│   ├──auth
│   │   └──login.html
│   └──crypto
│   │   ├──crypto_history.html
│   │   ├──crypto_stats.html
│   │   └──crypto.html
├──alembic.ini
├──docker-compose.yml
├──Dockerfile
├──Makefile
├──README.md
├──requirements.txt
├──.dockerignore
├──.env.example
└──.gitignore
```
## Запуск через Docker

```bash
docker-compose up --build
```

## Запуск через Kubernetes

```bash
make start
```


