import praw
import asyncio
import logging
import json
import re
import random
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import os

from pain_analyzer import PainPointAnalyzer
from database import DatabaseManager

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedditAPIParser:
    def __init__(self):
        self.analyzer = PainPointAnalyzer()
        self.db = DatabaseManager()
        self.db.init_database()
        
        # Загружаем переменные окружения
        load_dotenv()
        
        # Инициализация Reddit API с безопасными настройками
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT', 'E-commerce Pain Points Parser v1.0 by /u/your_username')
        )
        
        # Настройки для безопасного парсинга
        self.rate_limit_delay = 0.7  # 0.7 секунды между запросами (безопасно для 100 req/min)
        self.max_posts_per_subreddit = 25  # Ограничиваем количество постов
        self.max_comments_per_post = 5  # Ограничиваем комментарии
        self.request_count = 0
        self.last_request_time = 0
        
        # Подтверждаем подключение
        try:
            logger.info(f"Connected to Reddit as: {self.reddit.user.me() if self.reddit.user.me() else 'Read-only mode'}")
        except Exception as e:
            logger.warning(f"Reddit connection issue: {e}")
        
        # Субреддиты для парсинга (ограниченный список для безопасности)
        self.subreddits = [
            'ecommerce',
            'shopify',
            'woocommerce',
            'AmazonSeller',
            'FulfillmentByAmazon',
            'dropship',
            'entrepreneur',
            'smallbusiness'
        ]
        
        # Ключевые слова для поиска болей
        self.pain_keywords = [
            'problem', 'issue', 'struggle', 'difficult', 'challenge',
            'frustrated', 'stuck', 'help', 'advice', 'trouble',
            'error', 'bug', 'broken', 'not working', 'failed',
            'expensive', 'cost', 'budget', 'money', 'price',
            'time', 'slow', 'manual', 'tedious', 'repetitive',
            'confused', 'overwhelmed', 'lost', 'don\'t know'
        ]

    async def _rate_limit_wait(self):
        """Ожидание для соблюдения лимитов запросов"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            logger.debug(f"Rate limiting: waiting {sleep_time:.2f} seconds")
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
        
        # Логируем каждые 10 запросов
        if self.request_count % 10 == 0:
            logger.info(f"Made {self.request_count} requests to Reddit API")

    async def _safe_reddit_request(self, func, *args, **kwargs):
        """Безопасный запрос к Reddit API с соблюдением лимитов"""
        await self._rate_limit_wait()
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Reddit API request failed: {e}")
            return None

    async def crawl_reddit_posts(self, limit_per_subreddit: int = None) -> List[Dict[str, Any]]:
        """Парсинг постов с Reddit через API с соблюдением лимитов"""
        if limit_per_subreddit is None:
            limit_per_subreddit = self.max_posts_per_subreddit
            
        logger.info(f"Starting Reddit posts crawling with API (max {limit_per_subreddit} per subreddit)...")
        posts = []
        
        for subreddit_name in self.subreddits:
            try:
                logger.info(f"Crawling r/{subreddit_name}...")
                
                # Безопасное получение субреддита
                subreddit = await self._safe_reddit_request(
                    lambda: self.reddit.subreddit(subreddit_name)
                )
                
                if not subreddit:
                    logger.warning(f"Failed to get subreddit r/{subreddit_name}")
                    continue
                
                # Получаем горячие посты с ограничением
                hot_posts = await self._safe_reddit_request(
                    lambda: list(subreddit.hot(limit=limit_per_subreddit))
                )
                
                if not hot_posts:
                    logger.warning(f"No hot posts found in r/{subreddit_name}")
                    continue
                
                logger.info(f"Found {len(hot_posts)} posts in r/{subreddit_name}")
                
                # Обрабатываем посты
                for submission in hot_posts:
                    try:
                        post_data = await self._extract_post_data(submission)
                        if post_data and self._contains_pain_points(post_data):
                            posts.append(post_data)
                            logger.info(f"Found pain point in: {post_data['title'][:50]}...")
                    except Exception as e:
                        logger.warning(f"Error processing post {submission.id}: {e}")
                        continue
                
                # Дополнительная задержка между субреддитами
                logger.info(f"Completed r/{subreddit_name}, waiting before next subreddit...")
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error crawling r/{subreddit_name}: {e}")
                continue
        
        logger.info(f"Total Reddit posts collected: {len(posts)}")
        return posts

    async def _extract_post_data(self, submission) -> Optional[Dict[str, Any]]:
        """Извлечение данных из поста Reddit с безопасными запросами"""
        try:
            # Извлекаем комментарии с ограничением
            comments = []
            
            # Безопасное получение комментариев
            try:
                await self._safe_reddit_request(
                    lambda: submission.comments.replace_more(limit=0)
                )  # Убираем "load more comments"
                
                # Ограничиваем количество комментариев
                comment_count = 0
                for comment in submission.comments:
                    if comment_count >= self.max_comments_per_post:
                        break
                        
                    if hasattr(comment, 'body') and comment.body != '[deleted]' and len(comment.body) > 10:
                        comments.append({
                            'body': comment.body,
                            'score': comment.score,
                            'author': str(comment.author) if comment.author else 'deleted'
                        })
                        comment_count += 1
                        
                        # Небольшая задержка между комментариями
                        await asyncio.sleep(0.1)
                        
            except Exception as e:
                logger.warning(f"Error extracting comments from post {submission.id}: {e}")
            
            post_data = {
                'id': f"reddit_{submission.id}",
                'title': submission.title,
                'selftext': submission.selftext,
                'score': submission.score,
                'num_comments': submission.num_comments,
                'subreddit': str(submission.subreddit),
                'url': f"https://reddit.com{submission.permalink}",
                'author': str(submission.author) if submission.author else 'deleted',
                'created_utc': submission.created_utc,
                'comments': comments
            }
            
            return post_data
            
        except Exception as e:
            logger.warning(f"Error extracting post data: {e}")
            return None

    def _contains_pain_points(self, post_data: Dict[str, Any]) -> bool:
        """Проверяет, содержит ли пост болевые точки"""
        text_to_check = f"{post_data['title']} {post_data['selftext']}".lower()
        
        # Проверяем наличие ключевых слов
        pain_count = sum(1 for keyword in self.pain_keywords if keyword in text_to_check)
        
        # Проверяем комментарии
        for comment in post_data['comments']:
            comment_text = comment['body'].lower()
            pain_count += sum(1 for keyword in self.pain_keywords if keyword in comment_text)
        
        return pain_count >= 2  # Минимум 2 ключевых слова

    async def crawl_forum_posts(self) -> List[Dict[str, Any]]:
        """Парсинг форумов (используем Reddit как форум) с безопасными запросами"""
        logger.info("Starting forum posts crawling...")
        posts = []
        
        # Используем только первые 3 субреддита для безопасности
        limited_subreddits = self.subreddits[:3]
        
        for subreddit_name in limited_subreddits:
            try:
                logger.info(f"Crawling forum: r/{subreddit_name}")
                
                # Безопасное получение субреддита
                subreddit = await self._safe_reddit_request(
                    lambda: self.reddit.subreddit(subreddit_name)
                )
                
                if not subreddit:
                    continue
                
                # Ищем посты с определенными флейрами (ограниченное количество)
                search_results = await self._safe_reddit_request(
                    lambda: list(subreddit.search('flair:"Discussion" OR flair:"Question" OR flair:"Help"', limit=10))
                )
                
                if not search_results:
                    logger.info(f"No forum posts found in r/{subreddit_name}")
                    continue
                
                for submission in search_results:
                    try:
                        post_data = await self._extract_post_data(submission)
                        if post_data and self._contains_pain_points(post_data):
                            posts.append(post_data)
                    except Exception as e:
                        logger.warning(f"Error processing forum post {submission.id}: {e}")
                        continue
                
                # Дополнительная задержка между субреддитами
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"Error crawling forum r/{subreddit_name}: {e}")
                continue
        
        logger.info(f"Total forum posts collected: {len(posts)}")
        return posts

    async def crawl_blog_posts(self) -> List[Dict[str, Any]]:
        """Парсинг блогов (используем Reddit как источник блог-постов) с безопасными запросами"""
        logger.info("Starting blog posts crawling...")
        posts = []
        
        # Используем только первые 2 субреддита для безопасности
        limited_subreddits = self.subreddits[:2]
        
        for subreddit_name in limited_subreddits:
            try:
                logger.info(f"Crawling blog posts: r/{subreddit_name}")
                
                # Безопасное получение субреддита
                subreddit = await self._safe_reddit_request(
                    lambda: self.reddit.subreddit(subreddit_name)
                )
                
                if not subreddit:
                    continue
                
                # Получаем топ посты за месяц (ограниченное количество)
                top_posts = await self._safe_reddit_request(
                    lambda: list(subreddit.top(time_filter='month', limit=10))
                )
                
                if not top_posts:
                    logger.info(f"No top posts found in r/{subreddit_name}")
                    continue
                
                for submission in top_posts:
                    try:
                        # Проверяем, что пост достаточно длинный (как блог)
                        if len(submission.selftext) > 500:
                            post_data = await self._extract_post_data(submission)
                            if post_data and self._contains_pain_points(post_data):
                                posts.append(post_data)
                    except Exception as e:
                        logger.warning(f"Error processing blog post {submission.id}: {e}")
                        continue
                
                # Дополнительная задержка между субреддитами
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"Error crawling blog posts r/{subreddit_name}: {e}")
                continue
        
        logger.info(f"Total blog posts collected: {len(posts)}")
        return posts

    async def analyze_and_save_posts(self, posts: List[Dict[str, Any]]) -> None:
        """Анализ постов и сохранение в базу данных"""
        logger.info(f"Analyzing {len(posts)} posts...")
        
        for post in posts:
            try:
                # Анализируем пост
                pain_points = self.analyzer.analyze_text(
                    f"{post['title']} {post['selftext']}",
                    source_type="post",
                    source_id=post['id']
                )
                
                # Анализируем комментарии
                for comment in post['comments']:
                    comment_pain_points = self.analyzer.analyze_text(
                        comment['body'],
                        source_type="comment", 
                        source_id=f"{post['id']}_{comment['author']}"
                    )
                    pain_points.extend(comment_pain_points)
                
                # Сохраняем в базу данных
                self.db.save_post(post)
                
                for pain_point in pain_points:
                    self.db.save_pain_point(pain_point, post['id'])
                
                logger.info(f"Processed post: {post['title'][:50]}...")
                
            except Exception as e:
                logger.error(f"Error analyzing post {post.get('id', 'unknown')}: {e}")
                continue

    async def run_full_analysis(self) -> Dict[str, Any]:
        """Запуск полного анализа"""
        logger.info("Starting full pain points analysis...")
        
        # Собираем данные
        reddit_posts = await self.crawl_reddit_posts()
        forum_posts = await self.crawl_forum_posts()
        blog_posts = await self.crawl_blog_posts()
        
        # Объединяем все посты
        all_posts = reddit_posts + forum_posts + blog_posts
        
        # Анализируем и сохраняем
        await self.analyze_and_save_posts(all_posts)
        
        # Генерируем отчет
        report = self._generate_report()
        
        return {
            'total_posts': len(all_posts),
            'reddit_posts': len(reddit_posts),
            'forum_posts': len(forum_posts),
            'blog_posts': len(blog_posts),
            'report': report
        }

    def _generate_report(self) -> Dict[str, Any]:
        """Генерация отчета о найденных болях"""
        try:
            # Получаем статистику из базы данных
            pain_points = self.db.get_all_pain_points()
            
            if not pain_points:
                return {"error": "No pain points found"}
            
            # Группируем по категориям
            categories = {}
            for pain_point in pain_points:
                category = pain_point.get('category', 'Other')
                if category not in categories:
                    categories[category] = []
                categories[category].append(pain_point)
            
            # Топ болей
            top_pains = sorted(pain_points, key=lambda x: x.get('severity', 0), reverse=True)[:10]
            
            return {
                'total_pain_points': len(pain_points),
                'categories': {cat: len(points) for cat, points in categories.items()},
                'top_pains': top_pains,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {"error": str(e)}

# Функция для тестирования
async def test_reddit_parser():
    """Тестирование Reddit API парсера"""
    parser = RedditAPIParser()
    
    try:
        # Тестируем подключение
        logger.info("Testing Reddit API connection...")
        test_subreddit = parser.reddit.subreddit('ecommerce')
        test_posts = list(test_subreddit.hot(limit=1))
        
        if test_posts:
            logger.info(f"✅ Reddit API connection successful! Found {len(test_posts)} test posts")
        else:
            logger.warning("⚠️ Reddit API connected but no posts found")
        
        # Запускаем полный анализ
        logger.info("Running full analysis...")
        results = await parser.run_full_analysis()
        
        logger.info(f"Analysis complete! Results: {results}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_reddit_parser())
