#!/usr/bin/env python3
"""
Scrape CoinDesk & The Block News via RSS
"""

import feedparser
import json
import uuid
from datetime import datetime, timezone
import os
import sys

# RSS Feeds
FEEDS = {
    "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss",
    "the_block": "https://www.theblock.co/rss.xml"
}

def fetch_feed(name, url):
    print(f"Fetching {name} news from {url}...")
    try:
        # Use a user agent to avoid being blocked by Cloudflare/Bot protection
        feed = feedparser.parse(url)
        articles = []
        
        if not feed.entries:
            print(f"⚠️ No entries found for {name}. It might be protected or the URL changed.")
            return []
            
        for entry in feed.entries:
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
                "author": entry.get('author', name.split('_')[0].capitalize()),
                "tags": [name.capitalize(), "Crypto News"],
                "ticker": "BTC" # Default to BTC for crypto sources, will be refined in filter
            }
            articles.append(article)
            
        print(f"✅ Found {len(articles)} articles from {name}")
        return articles
    except Exception as e:
        print(f"❌ Error scraping {name}: {e}")
        return []

def main():
    # Scrape CoinDesk
    coindesk_news = fetch_feed("coindesk", FEEDS["coindesk"])
    with open(".tmp/raw_coindesk.json", 'w') as f:
        json.dump(coindesk_news, f, indent=2)
    
    # Scrape The Block
    the_block_news = fetch_feed("the_block", FEEDS["the_block"])
    with open(".tmp/raw_the_block.json", 'w') as f:
        json.dump(the_block_news, f, indent=2)

if __name__ == "__main__":
    os.makedirs(".tmp", exist_ok=True)
    main()
