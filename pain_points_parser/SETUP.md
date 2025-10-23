# Настройка Reddit API парсера

## Шаг 1: Создание Reddit приложения

1. Перейдите на https://www.reddit.com/prefs/apps
2. Нажмите "Create App" или "Create Another App"
3. Заполните форму:
   - **Name**: E-commerce Pain Points Parser
   - **App type**: Script
   - **Description**: Parser for e-commerce pain points analysis
   - **About URL**: (оставьте пустым)
   - **Redirect URI**: http://localhost:8080 (или любой другой)
4. Нажмите "Create app"
5. Скопируйте **Client ID** (под названием приложения)
6. Скопируйте **Client Secret** (в поле "secret")

## Шаг 2: Настройка переменных окружения

1. Скопируйте файл примера:
```bash
cp env_example.txt .env
```

2. Откройте `.env` файл и заполните:
```
REDDIT_CLIENT_ID=ваш_client_id_здесь
REDDIT_CLIENT_SECRET=ваш_client_secret_здесь
REDDIT_USER_AGENT=E-commerce Pain Points Parser v1.0
```

## Шаг 3: Установка зависимостей

```bash
pip install -r requirements.txt
```

## Шаг 4: Тестирование

```bash
python test_reddit_api.py
```

Если все настроено правильно, вы увидите:
```
✅ Подключение успешно! Найдено X тестовых постов
✅ Найдено X постов с болевыми точками
```

## Возможные проблемы

### Ошибка "Invalid credentials"
- Проверьте правильность Client ID и Client Secret
- Убедитесь, что приложение создано как "script"

### Ошибка "Forbidden"
- Убедитесь, что User Agent содержит уникальную строку
- Попробуйте изменить User Agent в .env файле

### Нет постов
- Проверьте интернет-соединение
- Убедитесь, что субреддиты существуют и доступны

## Готово!

Теперь вы можете использовать парсер для анализа болей e-commerce!
