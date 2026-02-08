#!/usr/bin/env python3
"""
Scrape Bloomberg & Reuters News via RSS
"""

import feedparser
import json
import uuid
from datetime import datetime, timezone
import os
import sys

# RSS Feeds
FEEDS = {
    "bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
    "reuters": "https://news.google.com/rss/search?q=site:reuters.com&hl=en-US&gl=US&ceid=US:en"
}

def fetch_feed(name, url):
    print(f"Fetching {name} news from {url}...")
    try:
        feed = feedparser.parse(url)
        articles = []
        
        for entry in feed.entries:
            # Basic info
            published = entry.get('published', '')
            if not published and 'published_parsed' in entry:
                published = datetime(*entry.published_parsed[:6]).replace(tzinfo=timezone.utc).isoformat()
            
            article = {
                "id": str(uuid.uuid4()),
                "source": name,
                "title": entry.title,
                "url": entry.link,
                "description": entry.get('summary', entry.get('description', '')),
                "published_at": published,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "author": entry.get('author', name.capitalize()),
                "tags": [name.capitalize(), "Financial News"],
                "ticker": "MIXED"
            }
            articles.append(article)
            
        print(f"✅ Found {len(articles)} articles from {name}")
        return articles
    except Exception as e:
        print(f"❌ Error scraping {name}: {e}")
        return []

def main():
    all_articles = []
    
    # Scrape Bloomberg
    bloomberg_news = fetch_feed("bloomberg", FEEDS["bloomberg"])
    with open(".tmp/raw_bloomberg.json", 'w') as f:
        json.dump(bloomberg_news, f, indent=2)
    
    # Scrape Reuters
    reuters_news = fetch_feed("reuters", FEEDS["reuters"])
    with open(".tmp/raw_reuters.json", 'w') as f:
        json.dump(reuters_news, f, indent=2)

if __name__ == "__main__":
    os.makedirs(".tmp", exist_ok=True)
    main()
