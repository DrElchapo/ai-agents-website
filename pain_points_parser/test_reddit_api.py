#!/usr/bin/env python3
"""
Тест Reddit API парсера
"""

import asyncio
import logging
from reddit_api_parser import RedditAPIParser

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция тестирования"""
    print("=" * 60)
    print("🧪 ТЕСТ REDDIT API ПАРСЕРА")
    print("=" * 60)
    
    try:
        # Создаем парсер
        parser = RedditAPIParser()
        
        # Тестируем подключение
        print("🔌 Тестируем подключение к Reddit API...")
        test_subreddit = parser.reddit.subreddit('ecommerce')
        test_posts = list(test_subreddit.hot(limit=1))
        
        if test_posts:
            print(f"✅ Подключение успешно! Найдено {len(test_posts)} тестовых постов")
        else:
            print("⚠️ Подключение есть, но посты не найдены")
        
        # Тестируем парсинг постов
        print("\n📡 Тестируем парсинг постов...")
        reddit_posts = await parser.crawl_reddit_posts(limit_per_subreddit=3)  # Ограничиваем для теста
        print(f"✅ Найдено {len(reddit_posts)} постов с болевыми точками")
        
        # Показываем примеры
        if reddit_posts:
            print("\n📋 Примеры найденных постов:")
            for i, post in enumerate(reddit_posts[:3], 1):
                print(f"{i}. {post['title'][:80]}...")
                print(f"   Субреддит: r/{post['subreddit']}")
                print(f"   Рейтинг: {post['score']}")
                print(f"   Комментарии: {post['num_comments']}")
                print()
        
        # Тестируем анализ
        print("🔍 Тестируем анализ болей...")
        await parser.analyze_and_save_posts(reddit_posts[:5])  # Анализируем только первые 5
        
        # Генерируем отчет
        print("📊 Генерируем отчет...")
        report = parser._generate_report()
        
        if 'error' not in report:
            print(f"✅ Отчет сгенерирован:")
            print(f"   Всего болей: {report['total_pain_points']}")
            print(f"   Категории: {report['categories']}")
        else:
            print(f"❌ Ошибка генерации отчета: {report['error']}")
        
        print("\n" + "=" * 60)
        print("🏁 Тестирование завершено!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
