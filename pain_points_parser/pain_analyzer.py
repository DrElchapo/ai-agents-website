import re
import json
from typing import List, Dict, Any, Tuple
from textblob import TextBlob
from loguru import logger
from config import PAIN_KEYWORDS, PAIN_CATEGORIES, SENTIMENT_THRESHOLDS, SCORING_WEIGHTS

class PainPointAnalyzer:
    def __init__(self):
        self.urgency_keywords = [
            "urgent", "asap", "immediately", "right now", "can't wait",
            "desperate", "critical", "emergency", "need help now"
        ]
        
        self.budget_keywords = [
            "budget", "money", "cost", "expensive", "cheap", "afford",
            "price", "pricing", "dollar", "$", "pay", "paid", "hire",
            "outsource", "freelancer", "agency"
        ]
    
    def analyze_text(self, text: str, source_type: str, source_id: str) -> List[Dict[str, Any]]:
        """Analyze text for pain points"""
        pain_points = []
        
        # Split into sentences
        sentences = self._split_into_sentences(text)
        
        for sentence in sentences:
            if self._is_pain_sentence(sentence):
                pain_point = self._extract_pain_point(sentence, source_type, source_id)
                if pain_point:
                    pain_points.append(pain_point)
        
        return pain_points
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _is_pain_sentence(self, sentence: str) -> bool:
        """Check if sentence contains pain indicators"""
        sentence_lower = sentence.lower()
        
        # Check for pain keywords
        for keyword in PAIN_KEYWORDS:
            if keyword.lower() in sentence_lower:
                return True
        
        # Check for negative sentiment
        blob = TextBlob(sentence)
        if blob.sentiment.polarity < SENTIMENT_THRESHOLDS["negative"]:
            return True
        
        return False
    
    def _extract_pain_point(self, sentence: str, source_type: str, source_id: str) -> Dict[str, Any]:
        """Extract pain point data from sentence"""
        try:
            # Find matching keywords
            found_keywords = self._find_keywords(sentence)
            
            # Calculate scores
            sentiment_score = self._calculate_sentiment_score(sentence)
            urgency_score = self._calculate_urgency_score(sentence)
            frequency_score = self._calculate_frequency_score(sentence, found_keywords)
            engagement_score = 0  # Will be set by caller
            budget_mention = self._has_budget_mention(sentence)
            
            # Categorize
            category, categories = self._categorize_pain_point(sentence, found_keywords)
            
            # Calculate total score
            total_score = (
                frequency_score * SCORING_WEIGHTS["frequency"] +
                sentiment_score * SCORING_WEIGHTS["sentiment"] +
                urgency_score * SCORING_WEIGHTS["urgency"] +
                (1 if budget_mention else 0) * SCORING_WEIGHTS["budget_mention"]
            )
            
            return {
                "source_type": source_type,
                "source_id": source_id,
                "text": sentence,
                "keywords": found_keywords,
                "category": category,
                "categories": categories,
                "sentiment_score": sentiment_score,
                "urgency_score": urgency_score,
                "frequency_score": frequency_score,
                "engagement_score": engagement_score,
                "budget_mention": budget_mention,
                "total_score": total_score
            }
            
        except Exception as e:
            logger.error(f"Error extracting pain point: {e}")
            return None
    
    def _find_keywords(self, sentence: str) -> List[str]:
        """Find pain keywords in sentence"""
        found_keywords = []
        sentence_lower = sentence.lower()
        
        for keyword in PAIN_KEYWORDS:
            if keyword.lower() in sentence_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _calculate_sentiment_score(self, sentence: str) -> float:
        """Calculate sentiment score (negative = higher pain)"""
        blob = TextBlob(sentence)
        # Convert to 0-1 scale where 1 = most negative
        return max(0, -blob.sentiment.polarity)
    
    def _calculate_urgency_score(self, sentence: str) -> float:
        """Calculate urgency score based on urgency keywords"""
        sentence_lower = sentence.lower()
        urgency_count = sum(1 for keyword in self.urgency_keywords if keyword in sentence_lower)
        return min(1.0, urgency_count * 0.3)  # Max score of 1.0
    
    def _calculate_frequency_score(self, sentence: str, keywords: List[str]) -> float:
        """Calculate frequency score based on keyword density"""
        word_count = len(sentence.split())
        keyword_count = len(keywords)
        return min(1.0, keyword_count / max(1, word_count) * 10)
    
    def _has_budget_mention(self, sentence: str) -> bool:
        """Check if sentence mentions budget/money"""
        sentence_lower = sentence.lower()
        return any(keyword in sentence_lower for keyword in self.budget_keywords)
    
    def _categorize_pain_point(self, sentence: str, keywords: List[str]) -> Tuple[str, Dict[str, float]]:
        """Categorize pain point and return confidence scores"""
        sentence_lower = sentence.lower()
        categories = {}
        
        for category, category_keywords in PAIN_CATEGORIES.items():
            matches = 0
            for keyword in category_keywords:
                if keyword.lower() in sentence_lower:
                    matches += 1
            
            # Calculate confidence based on matches
            confidence = min(1.0, matches / len(category_keywords) * 2)
            if confidence > 0.1:  # Only include if some confidence
                categories[category] = confidence
        
        # Find best category
        if categories:
            best_category = max(categories, key=categories.get)
        else:
            best_category = "general"
            categories["general"] = 0.1
        
        return best_category, categories
    
    def analyze_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple posts for pain points"""
        all_pain_points = []
        
        for post in posts:
            # Analyze post title and text
            post_text = f"{post.get('title', '')} {post.get('selftext', '')}"
            if post_text.strip():
                pain_points = self.analyze_text(post_text, "post", post['id'])
                all_pain_points.extend(pain_points)
            
            # Analyze comments
            for comment in post.get('comments', []):
                if comment.get('body'):
                    pain_points = self.analyze_text(comment['body'], "comment", comment['id'])
                    # Add engagement score based on comment score
                    for pain_point in pain_points:
                        pain_point['engagement_score'] = min(1.0, comment.get('score', 0) / 10)
                    all_pain_points.extend(pain_points)
        
        logger.info(f"Extracted {len(all_pain_points)} pain points from {len(posts)} posts")
        return all_pain_points
    
    def get_top_pain_points(self, pain_points: List[Dict[str, Any]], limit: int = 20) -> List[Dict[str, Any]]:
        """Get top pain points by score"""
        return sorted(pain_points, key=lambda x: x['total_score'], reverse=True)[:limit]
    
    def get_pain_points_by_category(self, pain_points: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
        """Filter pain points by category"""
        return [pp for pp in pain_points if pp['category'] == category]
    
    def generate_summary(self, pain_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of pain points analysis"""
        if not pain_points:
            return {"error": "No pain points found"}
        
        # Count by category
        category_counts = {}
        for pp in pain_points:
            category = pp['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Calculate averages
        avg_sentiment = sum(pp['sentiment_score'] for pp in pain_points) / len(pain_points)
        avg_urgency = sum(pp['urgency_score'] for pp in pain_points) / len(pain_points)
        avg_total = sum(pp['total_score'] for pp in pain_points) / len(pain_points)
        
        # Budget mentions
        budget_mentions = sum(1 for pp in pain_points if pp['budget_mention'])
        
        return {
            "total_pain_points": len(pain_points),
            "category_distribution": category_counts,
            "avg_sentiment_score": avg_sentiment,
            "avg_urgency_score": avg_urgency,
            "avg_total_score": avg_total,
            "budget_mentions": budget_mentions,
            "budget_mention_rate": budget_mentions / len(pain_points)
        }
