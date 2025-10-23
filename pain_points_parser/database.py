import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any
from loguru import logger
from config import DATABASE_CONFIG

class DatabaseManager:
    def __init__(self):
        self.db_path = DATABASE_CONFIG["db_path"]
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create posts table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {DATABASE_CONFIG['tables']['posts']} (
                id TEXT PRIMARY KEY,
                title TEXT,
                selftext TEXT,
                score INTEGER,
                num_comments INTEGER,
                created_utc INTEGER,
                subreddit TEXT,
                url TEXT,
                author TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create comments table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {DATABASE_CONFIG['tables']['comments']} (
                id TEXT PRIMARY KEY,
                post_id TEXT,
                body TEXT,
                score INTEGER,
                author TEXT,
                created_utc INTEGER,
                is_submitter BOOLEAN,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES {DATABASE_CONFIG['tables']['posts']} (id)
            )
        """)
        
        # Create pain points table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {DATABASE_CONFIG['tables']['pain_points']} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT,  -- 'post' or 'comment'
                source_id TEXT,
                text TEXT,
                keywords TEXT,  -- JSON array
                category TEXT,
                sentiment_score REAL,
                urgency_score REAL,
                frequency_score REAL,
                engagement_score REAL,
                budget_mention BOOLEAN,
                total_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create categories table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {DATABASE_CONFIG['tables']['categories']} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pain_point_id INTEGER,
                category TEXT,
                confidence REAL,
                FOREIGN KEY (pain_point_id) REFERENCES {DATABASE_CONFIG['tables']['pain_points']} (id)
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def save_posts(self, posts: List[Dict[str, Any]]):
        """Save posts to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for post in posts:
            try:
                cursor.execute(f"""
                    INSERT OR REPLACE INTO {DATABASE_CONFIG['tables']['posts']} 
                    (id, title, selftext, score, num_comments, created_utc, subreddit, url, author)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    post['id'],
                    post['title'],
                    post['selftext'],
                    post['score'],
                    post['num_comments'],
                    post['created_utc'],
                    post['subreddit'],
                    post['url'],
                    post['author']
                ))
                
                # Save comments
                for comment in post.get('comments', []):
                    cursor.execute(f"""
                        INSERT OR REPLACE INTO {DATABASE_CONFIG['tables']['comments']}
                        (id, post_id, body, score, created_utc, is_submitter)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        comment['id'],
                        post['id'],
                        comment['body'],
                        comment['score'],
                        comment['created_utc'],
                        comment['is_submitter']
                    ))
                
            except Exception as e:
                logger.error(f"Error saving post {post['id']}: {e}")
                continue
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(posts)} posts to database")
    
    def save_pain_points(self, pain_points: List[Dict[str, Any]]):
        """Save extracted pain points to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for pain_point in pain_points:
            try:
                cursor.execute(f"""
                    INSERT INTO {DATABASE_CONFIG['tables']['pain_points']}
                    (source_type, source_id, text, keywords, category, sentiment_score, 
                     urgency_score, frequency_score, engagement_score, budget_mention, total_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pain_point['source_type'],
                    pain_point['source_id'],
                    pain_point['text'],
                    json.dumps(pain_point['keywords']),
                    pain_point['category'],
                    pain_point['sentiment_score'],
                    pain_point['urgency_score'],
                    pain_point['frequency_score'],
                    pain_point['engagement_score'],
                    pain_point['budget_mention'],
                    pain_point['total_score']
                ))
                
                pain_point_id = cursor.lastrowid
                
                # Save categories
                for category, confidence in pain_point.get('categories', {}).items():
                    cursor.execute(f"""
                        INSERT INTO {DATABASE_CONFIG['tables']['categories']}
                        (pain_point_id, category, confidence)
                        VALUES (?, ?, ?)
                    """, (pain_point_id, category, confidence))
                
            except Exception as e:
                logger.error(f"Error saving pain point: {e}")
                continue
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(pain_points)} pain points to database")
    
    def get_pain_points_by_category(self, category: str = None) -> List[Dict[str, Any]]:
        """Get pain points, optionally filtered by category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute(f"""
                SELECT * FROM {DATABASE_CONFIG['tables']['pain_points']}
                WHERE category = ?
                ORDER BY total_score DESC
            """, (category,))
        else:
            cursor.execute(f"""
                SELECT * FROM {DATABASE_CONFIG['tables']['pain_points']}
                ORDER BY total_score DESC
            """)
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_top_pain_points(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get top pain points by score"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT * FROM {DATABASE_CONFIG['tables']['pain_points']}
            ORDER BY total_score DESC
            LIMIT ?
        """, (limit,))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get parsing statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count posts
        cursor.execute(f"SELECT COUNT(*) FROM {DATABASE_CONFIG['tables']['posts']}")
        post_count = cursor.fetchone()[0]
        
        # Count comments
        cursor.execute(f"SELECT COUNT(*) FROM {DATABASE_CONFIG['tables']['comments']}")
        comment_count = cursor.fetchone()[0]
        
        # Count pain points
        cursor.execute(f"SELECT COUNT(*) FROM {DATABASE_CONFIG['tables']['pain_points']}")
        pain_point_count = cursor.fetchone()[0]
        
        # Count by category
        cursor.execute(f"""
            SELECT category, COUNT(*) as count 
            FROM {DATABASE_CONFIG['tables']['pain_points']}
            GROUP BY category
            ORDER BY count DESC
        """)
        categories = dict(cursor.fetchall())
        
        # Average scores
        cursor.execute(f"""
            SELECT AVG(sentiment_score), AVG(urgency_score), AVG(total_score)
            FROM {DATABASE_CONFIG['tables']['pain_points']}
        """)
        avg_scores = cursor.fetchone()
        
        conn.close()
        
        return {
            "posts": post_count,
            "comments": comment_count,
            "pain_points": pain_point_count,
            "categories": categories,
            "avg_sentiment": avg_scores[0],
            "avg_urgency": avg_scores[1],
            "avg_total_score": avg_scores[2]
        }
    
    def get_all_pain_points(self) -> List[Dict[str, Any]]:
        """Get all pain points from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT * FROM {DATABASE_CONFIG['tables']['pain_points']}
            ORDER BY total_score DESC
        """)
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def save_post(self, post: Dict[str, Any]) -> None:
        """Save a post to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"""
                INSERT OR REPLACE INTO {DATABASE_CONFIG['tables']['posts']} 
                (id, title, selftext, score, num_comments, subreddit, url, author, created_utc)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post['id'],
                post['title'],
                post['selftext'],
                post['score'],
                post['num_comments'],
                post['subreddit'],
                post['url'],
                post['author'],
                post['created_utc']
            ))
            
            # Save comments
            for comment in post.get('comments', []):
                cursor.execute(f"""
                    INSERT OR REPLACE INTO {DATABASE_CONFIG['tables']['comments']}
                    (id, post_id, body, score, author)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    f"{post['id']}_{comment['author']}",
                    post['id'],
                    comment['body'],
                    comment['score'],
                    comment['author']
                ))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error saving post {post.get('id', 'unknown')}: {e}")
        finally:
            conn.close()
    
    def save_pain_point(self, pain_point: Dict[str, Any], post_id: str) -> None:
        """Save a single pain point to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"""
                INSERT INTO {DATABASE_CONFIG['tables']['pain_points']}
                (source_type, source_id, text, keywords, category, sentiment_score, 
                 urgency_score, frequency_score, engagement_score, budget_mention, total_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pain_point['source_type'],
                pain_point['source_id'],
                pain_point['text'],
                json.dumps(pain_point['keywords']),
                pain_point['category'],
                pain_point['sentiment_score'],
                pain_point['urgency_score'],
                pain_point['frequency_score'],
                pain_point['engagement_score'],
                pain_point['budget_mention'],
                pain_point['total_score']
            ))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error saving pain point: {e}")
        finally:
            conn.close()