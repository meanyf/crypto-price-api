import requests
import json
from datetime import datetime

# Конфигурация - должна совпадать с сервером
API_BASE_URL = "http://localhost:8000"
USERNAME = "johndoe"
PASSWORD = "secret"  # Пароль из вашей базы данных


def get_access_token():
    """
    Получает access token с сервера аутентификации
    """
    try:
        # Отправляем POST запрос для получения токена
        response = requests.post(
            f"{API_BASE_URL}/token",
            data={"username": USERNAME, "password": PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Проверяем успешность запроса
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            token_type = token_data.get("token_type")

            print("✅ Токен успешно получен!")
            print(f"Токен: {access_token}")
            print(f"Тип токена: {token_type}")

            # Сохраняем токен в файл для использования в других скриптах
            token_info = {
                "access_token": access_token,
                "token_type": token_type,
                "username": USERNAME,
                "obtained_at": datetime.now().isoformat(),
            }

            with open("token.json", "w") as f:
                json.dump(token_info, f, indent=2)
            print("✅ Токен сохранен в token.json")

            return access_token
        else:
            print(f"❌ Ошибка при получении токена: {response.status_code}")
            print(f"Сообщение: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print(
            "❌ Не удалось подключиться к серверу. Убедитесь, что сервер FastAPI запущен."
        )
        print("Запустите сервер: uvicorn main:app --reload")
        return None
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        return None


def test_protected_endpoints(access_token):
    """
    Тестирует полученный токен на защищенных endpoint'ах
    """
    if not access_token:
        return

    headers = {"Authorization": f"Bearer {access_token}"}

    # Тестируем endpoint /users/me/
    print("\n🧪 Тестирование endpoint /users/me/")
    try:
        response = requests.get(f"{API_BASE_URL}/users/me/", headers=headers)

        if response.status_code == 200:
            user_data = response.json()
            print("✅ Endpoint /users/me/ работает корректно!")
            print(f"Данные пользователя: {json.dumps(user_data, indent=2)}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"Сообщение: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка при тестировании /users/me/: {e}")

    # Тестируем endpoint /users/me/items/
    print("\n🧪 Тестирование endpoint /users/me/items/")
    try:
        response = requests.get(f"{API_BASE_URL}/users/me/items/", headers=headers)

        if response.status_code == 200:
            items_data = response.json()
            print("✅ Endpoint /users/me/items/ работает корректно!")
            print(f"Данные items: {json.dumps(items_data, indent=2)}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"Сообщение: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка при тестировании /users/me/items/: {e}")


if __name__ == "__main__":
    print("🔐 Получение access token...")
    print("Используемые учетные данные:")
    print(f"Username: {USERNAME}")
    print(f"Password: {PASSWORD}")
    print("-" * 50)

    token = get_access_token()

    if token:
        print("\n" + "=" * 50)
        test_protected_endpoints(token)
    else:
        print("\n❌ Не удалось получить токен")
