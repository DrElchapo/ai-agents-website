# E-commerce Pain Points Parser (Reddit API)

Парсер для поиска реальных болей и проблем в e-commerce через анализ Reddit с помощью официального API.

## Возможности

- **Reddit API** - использует официальный PRAW для надежного парсинга
- **Множество субреддитов** - анализирует 10+ сообществ e-commerce
- **AI-анализ** - автоматическое выявление проблемных мест с помощью NLP
- **Категоризация** - группировка болей по типам (операционные, аналитические, etc.)
- **Оценка важности** - ранжирование по частоте, сентименту, срочности
- **База данных** - сохранение всех данных для дальнейшего анализа
- **Отчеты** - генерация детальных отчетов с рекомендациями

## Установка

1. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

2. **Создайте Reddit приложение:**
   - Перейдите на https://www.reddit.com/prefs/apps
   - Нажмите "Create App" или "Create Another App"
   - Выберите "script" тип
   - Скопируйте Client ID и Client Secret

3. **Настройте переменные окружения:**
```bash
cp env_example.txt .env
```

Заполните `.env` файл:
```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=E-commerce Pain Points Parser v1.0
```

## Использование

### Быстрый тест
```bash
python test_reddit_api.py
```

### Полный парсинг
```python
import asyncio
from reddit_api_parser import RedditAPIParser

async def main():
    parser = RedditAPIParser()
    results = await parser.run_full_analysis()
    print(f"Найдено {results['total_posts']} постов")

asyncio.run(main())
```

## Структура данных

### Pain Point Object
```python
{
    "source_type": "post|comment",
    "source_id": "reddit_id",
    "text": "I spend 3 hours every day manually updating prices...",
    "keywords": ["manual", "hours", "every day"],
    "category": "operational",
    "sentiment_score": 0.8,  # 0-1, чем выше = больше боли
    "urgency_score": 0.6,    # 0-1, срочность
    "frequency_score": 0.9,  # 0-1, частота упоминаний
    "budget_mention": True,  # упоминание денег/бюджета
    "total_score": 0.75      # общий балл важности
}
```

## Субреддиты

Парсер анализирует следующие субреддиты:
- r/ecommerce
- r/shopify
- r/woocommerce
- r/AmazonSeller
- r/FulfillmentByAmazon
- r/dropship
- r/entrepreneur
- r/smallbusiness
- r/startups
- r/marketing

## Категории болей

- **operational** - рутинные задачи (инвентарь, заказы, загрузка товаров)
- **analytical** - аналитика и отчеты
- **communication** - общение с клиентами
- **technical** - технические проблемы
- **marketing** - маркетинг и продвижение
- **financial** - ценообразование и финансы

## Настройка

### Добавление новых субреддитов
Отредактируйте `reddit_api_parser.py`:
```python
self.subreddits = [
    'ecommerce',
    'shopify', 
    'your_new_subreddit'
]
```

### Добавление ключевых слов
```python
self.pain_keywords = [
    'problem', 'issue', 'struggle',
    'your_new_keyword'
]
```

## Результаты

После запуска создаются:

1. **pain_points.db** - SQLite база с данными
2. **pain_points_report.md** - детальный отчет
3. **pain_points.log** - лог выполнения

### Пример отчета
```
# E-commerce Pain Points Analysis Report

## Summary
- Total pain points found: 247
- Budget mention rate: 34.2%
- Average sentiment score: 0.67

## Top Categories
- operational: 89 (36.0%)
- analytical: 67 (27.1%)
- communication: 45 (18.2%)

## Top Pain Points
1. [operational] I spend 3 hours every day manually updating prices... (Score: 0.89)
2. [analytical] Creating reports takes forever and I always miss important data... (Score: 0.85)
```

## API Reference

### RedditAPIParser
- `crawl_reddit_posts(limit_per_subreddit)` - парсинг Reddit постов
- `crawl_forum_posts()` - парсинг форумов
- `crawl_blog_posts()` - парсинг блог-постов
- `run_full_analysis()` - полный анализ всех источников
- `analyze_and_save_posts(posts)` - анализ и сохранение

### PainPointAnalyzer
- `analyze_text(text)` - анализ текста
- `analyze_posts(posts)` - анализ массива постов
- `get_top_pain_points(points, limit)` - топ болей
- `generate_summary(points)` - сводка анализа

### DatabaseManager
- `save_post(post)` - сохранение поста
- `save_pain_point(pain_point, post_id)` - сохранение боли
- `get_all_pain_points()` - получение всех болей
- `get_statistics()` - статистика парсинга

## Troubleshooting

### Ошибка Reddit API
```
praw.exceptions.InvalidInvocation: Invalid credentials
```
**Решение:** Проверьте правильность Client ID и Client Secret в `.env` файле

### Нет данных
```
No posts found
```
**Решение:** Проверьте интернет-соединение и доступность Reddit

### Медленный парсинг
**Решение:** Reddit API имеет лимиты запросов, парсер автоматически делает паузы

## Лицензия

MIT License