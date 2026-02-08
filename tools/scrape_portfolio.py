#!/usr/bin/env python3
"""
Portfolio News Scraper
Scrapes latest news specifically for: GOOG, EQIX, U, TDOC, BTC
"""

import feedparser
import json
import uuid
from datetime import datetime, timezone
import sys
import os
from html import unescape
import re

# Configuration
SOURCE_NAME = "portfolio"
# Portfolio Configuration
TICKERS = ["GOOG", "EQIX", "U", "TDOC", "BTC-USD", "ETH-USD", "LINK-USD", "AVAX-USD"]
# Common Search Queries for broader coverage
SEARCH_QUERIES = [
    "(GOOG OR Alphabet OR Google)",
    "(EQIX OR Equinix)",
    "(Unity Software OR U STOCK OR Unity Engine)",
    "(TDOC OR Teladoc Health)",
    "(Bitcoin OR BTC)",
    "(Ethereum OR ETH)",
    "(Chainlink OR LINK crypto)",
    "(Avalanche AVAX crypto)"
]
# Map tickers to friendly names for better searching/filtering
TICKER_MAP = {
    "GOOG": ["Alphabet", "Google"],
    "EQIX": ["Equinix"],
    "U": ["Unity Software", "Unity Technologies"],
    "TDOC": ["Teladoc"],
    "BTC-USD": ["Bitcoin", "BTC"],
    "ETH-USD": ["Ethereum", "ETH"],
    "LINK-USD": ["Chainlink", "LINK crypto"],
    "AVAX-USD": ["Avalanche", "AVAX crypto"]
}

OUTPUT_FILE = ".tmp/raw_portfolio.json"
ERROR_LOG = ".tmp/scraper_errors.log"

def log_error(message):
    """Log error to file"""
    timestamp = datetime.now(timezone.utc).isoformat()
    os.makedirs(os.path.dirname(ERROR_LOG), exist_ok=True)
    with open(ERROR_LOG, 'a') as f:
        f.write(f"[{timestamp}] [Portfolio] {message}\n")
    print(f"ERROR: {message}", file=sys.stderr)

def fetch_ticker_news(ticker):
    """Fetch RSS feed for a specific ticker from Yahoo Finance"""
    # Yahoo Finance RSS for specific tickers
    url = f"https://finance.yahoo.com/quote/{ticker}/rss"
    articles = []
    
    try:
        print(f"Fetching news for {ticker}...")
        feed = feedparser.parse(url)
        
        if feed.bozo:
            log_error(f"RSS parsing warning for {ticker}: {feed.bozo_exception}")
            
        print(f"Found {len(feed.entries)} entries for {ticker}")
        
        for entry in feed.entries:
            title = entry.get('title', '').strip()
            if not title:
                continue
                
            url_link = entry.get('link', '')
            description = entry.get('summary', '') or entry.get('description', '')
            
            if description:
                description = re.sub('<[^<]+?>', '', description)
                description = unescape(description).strip()
                
            # Date parsing
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
            else:
                published_at = datetime.now(timezone.utc).isoformat()
                
            article = {
                "id": str(uuid.uuid4()),
                "source": "yahoo_finance",
                "ticker": ticker.split('-')[0], # Store clean ticker
                "title": title,
                "url": url_link,
                "description": description[:200] if description else None,
                "published_at": published_at,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "content_preview": description[:200] if description else None,
                "author": entry.get('author', 'Yahoo Finance'),
                "tags": [ticker, "Portfolio"],
                "image_url": None
            }
            articles.append(article)
            
    except Exception as e:
        log_error(f"Error fetching news for {ticker}: {e}")
        
    return articles

def fetch_google_search_news():
    """Fetch news from Google News for the entire portfolio"""
    import urllib.parse
    
    query_parts = []
    for ticker, names in TICKER_MAP.items():
        search_terms = [ticker.split('-')[0]] + names
        query_parts.append(f"({' OR '.join(search_terms)})")
    
    query = " OR ".join(query_parts)
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    articles = []
    try:
        print(f"Fetching Google News for portfolio: {query[:50]}...")
        feed = feedparser.parse(url)
        
        if not hasattr(feed, 'entries') or not feed.entries:
            print(f"No entries found in Google News for portfolio search.")
            return []
            
        print(f"Found {len(feed.entries)} entries in Google News")
        
        for entry in feed.entries:
            title = entry.get('title', '').strip()
            if not title:
                continue
                
            # Determine which ticker this article belongs to
            matched_ticker = "PORTFOLIO"
            content_text = (title + " " + (entry.get('summary', '') or '')).upper()
            
            for ticker_key, names in TICKER_MAP.items():
                clean_ticker = ticker_key.split('-')[0].upper()
                if clean_ticker in content_text or any(n.upper() in content_text for n in names):
                    matched_ticker = clean_ticker
                    break

            # Extract date
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
            else:
                published_at = datetime.now(timezone.utc).isoformat()

            article = {
                "id": str(uuid.uuid4()),
                "source": "google_finance",
                "ticker": matched_ticker,
                "title": title,
                "url": entry.get('link', ''),
                "description": entry.get('summary', '')[:200] if entry.get('summary') else None,
                "published_at": published_at,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "content_preview": entry.get('summary', '')[:200] if entry.get('summary') else None,
                "author": entry.get('source', {}).get('title', 'Google News'),
                "tags": [matched_ticker, "Portfolio"],
                "image_url": None
            }
            articles.append(article)
            
    except Exception as e:
        log_error(f"Error fetching Google News: {e}")
        
    return articles

def main():
    print("=" * 60)
    print("Portfolio News Scraper")
    print("=" * 60)
    
    all_articles = []
    
    # 1. Fetch from Yahoo for each ticker
    for ticker in TICKERS:
        ticker_articles = fetch_ticker_news(ticker)
        all_articles.extend(ticker_articles)
        
    # 2. Fetch from Google Search
    google_articles = fetch_google_search_news()
    all_articles.extend(google_articles)
    
    if not all_articles:
        print("No articles found for your portfolio.")
        sys.exit(0)
        
    # Save to file
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Successfully scraped {len(all_articles)} portfolio articles")
    sys.exit(0)

if __name__ == "__main__":
    main()
