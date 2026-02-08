#!/usr/bin/env python3
"""
AI Rundown RSS Scraper
Scrapes latest AI news articles from therundown.ai RSS feed
"""

import feedparser
import json
import uuid
from datetime import datetime, timezone
import sys
import os

# Configuration
SOURCE_NAME = "ai_rundown"
RSS_URL = "https://www.therundown.ai/feed"
OUTPUT_FILE = ".tmp/raw_ai_rundown.json"
ERROR_LOG = ".tmp/scraper_errors.log"

def log_error(message):
    """Log error to file"""
    timestamp = datetime.now(timezone.utc).isoformat()
    os.makedirs(os.path.dirname(ERROR_LOG), exist_ok=True)
    with open(ERROR_LOG, 'a') as f:
        f.write(f"[{timestamp}] [AIRundown] {message}\n")
    print(f"ERROR: {message}", file=sys.stderr)

def fetch_rss():
    """Fetch and parse RSS feed"""
    try:
        print(f"Fetching RSS feed: {RSS_URL}")
        feed = feedparser.parse(RSS_URL)
        
        if feed.bozo:
            log_error(f"RSS parsing warning: {feed.bozo_exception}")
        
        print(f"Found {len(feed.entries)} entries in RSS feed")
        return feed
    except Exception as e:
        log_error(f"Error fetching RSS: {e}")
        return None

def parse_articles(feed):
    """Parse articles from RSS feed"""
    if not feed or not feed.entries:
        return []
    
    articles = []
    
    for entry in feed.entries:
        try:
            # Extract title
            title = entry.get('title', '').strip()
            if not title:
                continue
            
            # Extract URL
            url = entry.get('link', '')
            
            # Extract description/summary
            description = entry.get('summary', '') or entry.get('description', '')
            # Clean HTML tags from description
            if description:
                from html import unescape
                import re
                description = re.sub('<[^<]+?>', '', description)
                description = unescape(description).strip()
            
            # Extract published date
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
            else:
                published_at = datetime.now(timezone.utc).isoformat()
            
            # Extract author
            author = entry.get('author', 'The Rundown AI')
            
            # Extract tags
            tags = ['AI', 'Newsletter']
            if hasattr(entry, 'tags'):
                tags.extend([tag.term for tag in entry.tags])
            
            article = {
                "id": str(uuid.uuid4()),
                "source": SOURCE_NAME,
                "title": title,
                "url": url,
                "description": description[:200] if description else None,
                "published_at": published_at,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "content_preview": description[:200] if description else None,
                "author": author,
                "tags": list(set(tags)),
                "image_url": None
            }
            
            articles.append(article)
            print(f"Parsed: {title[:50]}...")
            
        except Exception as e:
            log_error(f"Error parsing entry: {e}")
            continue
    
    return articles

def save_articles(articles):
    """Save articles to JSON file"""
    try:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(articles)} articles to {OUTPUT_FILE}")
        return True
    except Exception as e:
        log_error(f"Error saving articles: {e}")
        return False

def main():
    """Main scraper function"""
    print("=" * 60)
    print("AI Rundown RSS Scraper")
    print("=" * 60)
    
    # Fetch RSS
    feed = fetch_rss()
    if not feed:
        print("Failed to fetch RSS feed. Exiting.")
        sys.exit(1)
    
    # Parse articles
    articles = parse_articles(feed)
    
    if not articles:
        print("No articles found in RSS feed.")
        sys.exit(1)
    
    # Save to file
    if save_articles(articles):
        print(f"✅ Successfully scraped {len(articles)} articles from AI Rundown")
        sys.exit(0)
    else:
        print("Failed to save articles.")
        sys.exit(1)

if __name__ == "__main__":
    main()
