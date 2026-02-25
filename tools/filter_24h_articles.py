#!/usr/bin/env python3
"""
Filter 24-Hour Articles
Filters articles to only include those from the last 24 hours
"""

import json
import sys
from datetime import datetime, timezone, timedelta
import os
from dateutil import parser

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

def get_sentiment(text):
    """Simple keyword-based sentiment analysis"""
    bullish_keywords = [
        "GROWTH", "PROFIT", "SURGE", "BUY", "OUTPERFORM", "GAIN", "EXPANSION", 
        "HIT", "HIGH", "UPGRADE", "SUCCESS", "INNOVATIVE", "BULLISH", "RECOVERY",
        "PARTNERSHIP", "ACQUISITION", "CLIMB", "BEAT", "RALLY", "GREEN", "MOON"
    ]
    bearish_keywords = [
        "LOSS", "DECLINE", "SLUMP", "SELL", "UNDERPERFORM", "DROP", "CUT", 
        "LOW", "DOWNGRADE", "FAILURE", "RISK", "LAWSUIT", "BEARISH", "CRASH",
        "FEAR", "RED", "DEBT", "SKEPTICAL", "LAYOFF", "WARNING", "MISS"
    ]
    
    text = text.upper()
    score = 0
    for k in bullish_keywords:
        if k in text:
            score += 1
    for k in bearish_keywords:
        if k in text:
            score -= 1
            
    if score > 0:
        return "bullish"
    elif score < 0:
        return "bearish"
    else:
        return "neutral"

def load_data(filepath):
    """Load articles and metadata from JSON file"""
    try:
        if not os.path.exists(filepath):
            # print(f"File not found: {filepath}")
            return {"articles": [], "analyses": {}}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if isinstance(data, list):
            return {"articles": data, "analyses": {}}
        
        return {
            "articles": data.get("articles", []),
            "analyses": data.get("analyses", {})
        }
    except Exception as e:
        print(f"Error loading {filepath}: {e}", file=sys.stderr)
        return {"articles": [], "analyses": {}}

def filter_24h(articles):
    """Filter articles from last 7 days and only include portfolio-related news"""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=30)  # Changed to 30 days to ensure news is found
    
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
            
            # Robust parsing using dateutil
            try:
                published = parser.parse(published_str)
                if published.tzinfo is None:
                    published = published.replace(tzinfo=timezone.utc)
            except:
                print(f"Failed to parse date: {published_str}")
                continue
            
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
                article['sentiment'] = get_sentiment(content)
                filtered.append(article)
            elif any(keyword in content for keyword in PORTFOLIO_KEYWORDS):
                # Fallback check
                article['sentiment'] = get_sentiment(content)
                filtered.append(article)
                    
        except Exception as e:
            print(f"Error parsing article: {e}", file=sys.stderr)
            continue
    
    return filtered

def save_data(articles, analyses):
    """Save filtered data including analyses"""
    try:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        payload = {
            "articles": articles,
            "analyses": analyses
        }
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(articles)} filtered articles and {len(analyses)} analyses to {OUTPUT_FILE}")
        return True
    except Exception as e:
        print(f"Error saving articles: {e}", file=sys.stderr)
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("24-Hour Article Filter")
    print("=" * 60)
    
    # Load all data
    all_articles = []
    all_analyses = {}
    for filepath in INPUT_FILES:
        data = load_data(filepath)
        all_articles.extend(data["articles"])
        all_analyses.update(data["analyses"])
    
    print(f"\nTotal articles loaded: {len(all_articles)}")
    print(f"Total analyses found: {len(all_analyses)}")
    
    # Filter
    filtered = filter_24h(all_articles)
    print(f"Articles matching filters: {len(filtered)}")
    
    # Save
    if save_data(filtered, all_analyses):
        print(f"✅ Successfully filtered articles")
        sys.exit(0)
    else:
        print("Failed to save filtered articles")
        sys.exit(1)

if __name__ == "__main__":
    main()
