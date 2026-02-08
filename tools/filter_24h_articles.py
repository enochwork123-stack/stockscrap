#!/usr/bin/env python3
"""
Filter 24-Hour Articles
Filters articles to only include those from the last 24 hours
"""

import json
import sys
from datetime import datetime, timezone, timedelta
import os

INPUT_FILES = [
    ".tmp/raw_portfolio.json",
    ".tmp/raw_bloomberg.json",
    ".tmp/raw_reuters.json",
    ".tmp/raw_coindesk.json",
    ".tmp/raw_the_block.json",
    ".tmp/raw_yahoo_finance.json",
    ".tmp/raw_google_finance.json"
]

PORTFOLIO_KEYWORDS = [
    "GOOG", "ALPHABET", "GOOGLE", 
    "EQIX", "EQUINIX", 
    "UNITY", "U STOCK", "U.US",
    "TDOC", "TELADOC", 
    "BTC", "BITCOIN", "ETH", "ETHEREUM", 
    "LINK", "CHAINLINK", "AVAX", "AVALANCHE"
]
OUTPUT_FILE = ".tmp/filtered_articles.json"

def load_articles(filepath):
    """Load articles from JSON file"""
    try:
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        print(f"Loaded {len(articles)} articles from {filepath}")
        return articles
    except Exception as e:
        print(f"Error loading {filepath}: {e}", file=sys.stderr)
        return []

def filter_24h(articles):
    """Filter articles from last 7 days and only include portfolio-related news"""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=7)  # Changed to 7 days for demo
    
    # Map keywords to specific ticker codes
    TICKER_TAG_MAP = {
        "GOOG": ["GOOG", "ALPHABET", "GOOGLE"],
        "EQIX": ["EQIX", "EQUINIX"],
        "U": ["UNITY", "U STOCK", "U.US"],
        "TDOC": ["TDOC", "TELADOC"],
        "BTC": ["BTC", "BITCOIN"],
        "ETH": ["ETH", "ETHEREUM"],
        "LINK": ["LINK", "CHAINLINK"],
        "AVAX": ["AVAX", "AVALANCHE"]
    }

    filtered = []
    for article in articles:
        try:
            # Date filter
            published_str = article.get('published_at')
            if not published_str:
                continue
            
            published = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
            
            if published < cutoff:
                continue
                
            # Strict Portfolio Filter
            title = (article.get('title') or "").upper()
            description = (article.get('description') or "").upper()
            author = (article.get('author') or "").upper()
            content = f"{title} {description} {author}"
            
            # Identify which ticker this belongs to
            matched_ticker = article.get('ticker')
            
            for ticker, keywords in TICKER_TAG_MAP.items():
                if any(k in content for k in keywords):
                    matched_ticker = ticker
                    break
            
            if matched_ticker and matched_ticker != "MIXED":
                article['ticker'] = matched_ticker
                filtered.append(article)
            elif any(keyword in content for keyword in PORTFOLIO_KEYWORDS):
                # Fallback check
                filtered.append(article)
                    
        except Exception as e:
            print(f"Error parsing article: {e}", file=sys.stderr)
            continue
    
    return filtered

def save_articles(articles):
    """Save filtered articles"""
    try:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(articles)} filtered articles to {OUTPUT_FILE}")
        return True
    except Exception as e:
        print(f"Error saving articles: {e}", file=sys.stderr)
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("24-Hour Article Filter")
    print("=" * 60)
    
    # Load all articles
    all_articles = []
    for filepath in INPUT_FILES:
        articles = load_articles(filepath)
        all_articles.extend(articles)
    
    print(f"\nTotal articles loaded: {len(all_articles)}")
    
    # Filter to last 24 hours
    filtered = filter_24h(all_articles)
    print(f"Articles from last 24 hours: {len(filtered)}")
    
    # Save
    if save_articles(filtered):
        print(f"✅ Successfully filtered articles")
        sys.exit(0)
    else:
        print("Failed to save filtered articles")
        sys.exit(1)

if __name__ == "__main__":
    main()
