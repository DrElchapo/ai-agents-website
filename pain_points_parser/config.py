# Configuration for pain points parser

# Reddit API credentials (get from https://www.reddit.com/prefs/apps)
REDDIT_CONFIG = {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret", 
    "user_agent": "EcommercePainPointsBot/1.0"
}

# Subreddits to monitor
SUBREDDITS = [
    "ecommerce",
    "shopify", 
    "AmazonSeller",
    "Entrepreneur",
    "smallbusiness",
    "FulfillmentByAmazon",
    "dropship",
    "marketing",
    "startups"
]

# Keywords to search for pain points
PAIN_KEYWORDS = [
    # Time-consuming tasks
    "manual", "manual process", "manually", "hand", "by hand",
    "time consuming", "takes too long", "too much time", "waste time",
    "hours", "every day", "daily", "repetitive", "tedious", "boring",
    
    # Problems and frustrations
    "problem", "issue", "struggle", "difficult", "hard", "challenging",
    "frustrated", "annoying", "pain", "headache", "nightmare",
    "overwhelmed", "burnout", "stressed", "tired",
    
    # Inefficiency
    "inefficient", "slow", "error", "mistake", "wrong", "broken",
    "doesn't work", "not working", "failed", "failure",
    "complicated", "complex", "confusing", "unclear",
    
    # Scaling issues
    "can't scale", "scaling", "growing", "hiring", "outsource",
    "need help", "need someone", "need automation", "need tool",
    "expensive", "cost", "budget", "money", "afford",
    
    # Specific e-commerce tasks
    "inventory", "stock", "products", "upload", "listing",
    "orders", "shipping", "fulfillment", "customer service",
    "pricing", "competitors", "analytics", "reports", "data",
    "email", "marketing", "ads", "social media", "content"
]

# Pain point categories
PAIN_CATEGORIES = {
    "operational": [
        "inventory", "stock", "products", "upload", "listing", "orders",
        "shipping", "fulfillment", "manual", "repetitive", "daily tasks"
    ],
    "analytical": [
        "analytics", "reports", "data", "tracking", "metrics", "insights",
        "performance", "roi", "conversion", "sales data"
    ],
    "communication": [
        "customer service", "email", "support", "communication", "response",
        "follow up", "notifications", "alerts"
    ],
    "technical": [
        "integration", "api", "technical", "coding", "development", "setup",
        "configuration", "maintenance", "updates", "bugs"
    ],
    "marketing": [
        "marketing", "ads", "social media", "content", "promotion", "seo",
        "traffic", "conversion", "branding", "campaigns"
    ],
    "financial": [
        "pricing", "competitors", "cost", "budget", "expensive", "money",
        "profit", "revenue", "margins", "pricing strategy"
    ]
}

# Database configuration
DATABASE_CONFIG = {
    "db_path": "pain_points.db",
    "tables": {
        "posts": "reddit_posts",
        "comments": "reddit_comments", 
        "pain_points": "extracted_pain_points",
        "categories": "pain_categories"
    }
}

# Parsing settings
PARSING_CONFIG = {
    "max_posts_per_subreddit": 100,
    "max_comments_per_post": 50,
    "min_score": 1,  # Minimum upvotes
    "time_filter": "month",  # day, week, month, year, all
    "delay_between_requests": 1,  # seconds
    "max_retries": 3
}

# Sentiment analysis thresholds
SENTIMENT_THRESHOLDS = {
    "negative": -0.1,
    "neutral": 0.1,
    "positive": 0.1
}

# Pain point scoring weights
SCORING_WEIGHTS = {
    "frequency": 0.3,      # How often mentioned
    "sentiment": 0.2,      # How negative the sentiment
    "engagement": 0.2,     # Upvotes, comments, replies
    "urgency": 0.15,       # Words like "urgent", "asap", "immediately"
    "budget_mention": 0.15 # Mentions of money, budget, cost
}
