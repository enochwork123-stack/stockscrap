#!/usr/bin/env python3
"""
Portfolio News Scraper - Senior Search implementation
Scrapes latest news specifically for: GOOG, EQIX, U, TDOC, BTC, ETH, LINK, AVAX
Using high-precision search and scoring-based ticker matching.
"""

import feedparser
import json
import uuid
from datetime import datetime, timezone
import sys
import os
from html import unescape
import re
import socket

# Set global timeout for all socket operations (30 seconds)
socket.setdefaulttimeout(30)

# Configuration
SOURCE_NAME = "portfolio"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
TICKERS = ["GOOG", "EQIX", "U", "TDOC", "BTC-USD", "ETH-USD", "LINK-USD", "AVAX-USD"]
OUTPUT_FILE = "data/dashboard_payload.js" # This will be managed by deduplicate_articles.py later, but we save raw here
RAW_OUTPUT = ".tmp/raw_portfolio.json"
ERROR_LOG = ".tmp/scraper_errors.log"

def log_error(message):
    """Log error to file"""
    timestamp = datetime.now(timezone.utc).isoformat()
    os.makedirs(os.path.dirname(ERROR_LOG), exist_ok=True)
    with open(ERROR_LOG, 'a') as f:
        f.write(f"[{timestamp}] [Portfolio] {message}\n")
    print(f"ERROR: {message}", file=sys.stderr)

def get_simple_sentiment(text):
    """Simple keyword-based sentiment analysis"""
    bullish = ["growth", "profit", "surge", "buy", "outperform", "gain", "expansion", "beat", "rally", "recovery", "partnership"]
    bearish = ["loss", "decline", "slump", "sell", "underperform", "drop", "cut", "risk", "failure", "miss", "debt"]
    text = text.lower()
    score = sum(2 for w in bullish if w in text) - sum(2 for w in bearish if w in text)
    return "bullish" if score > 0 else ("bearish" if score < 0 else "neutral")

def assign_ticker(title, summary):
    """
    Advanced scoring-based ticker assignment for high precision.
    Uses primary terms, context clues, and decoy penalties.
    """
    text = (title + " " + summary).upper()
    
    # Advanced profiles for disambiguation
    PROFILES = {
        "GOOG": {
            "primary": ["ALPHABET INC", "GOOGLE", "GOOGL"],
            "context": ["SEARCH", "YOUTUBE", "CLOUD", "AI", "SUNDAR PICHAI", "AD REVENUE", "NASDAQ:GOOG"],
            "decoys": ["GOOGLE MAPS SEARCH", "GOOGLE ACCOUNT", "GOOGLE DRIVE", "GOOGLE PLAY STORE"]
        },
        "EQIX": {
            "primary": ["EQUINIX", "EQIX"],
            "context": ["DATA CENTER", "REIT", "COLOCATION", "INTERCONNECTION", "PLATFORM EQUINIX", "CHARLES MEYERS"],
            "decoys": []
        },
        "U": {
            "primary": ["UNITY SOFTWARE", "UNITY TECHNOLOGIES"],
            "context": ["GAME ENGINE", "RT3D", "UNITY STOCK", "IRONSOURCE", "CREATE SOLUTIONS", "WHITEHURST"],
            "decoys": ["UNITY CHURCH", "NATIONAL UNITY", "SPIRIT OF UNITY", "UNITY DAY"]
        },
        "TDOC": {
            "primary": ["TELADOC", "TDOC"],
            "context": ["TELEHEALTH", "VIRTUAL CARE", "LIVONGO", "REMOTE MONITORING", "GOREVIC"],
            "decoys": []
        },
        "BTC": {
            "primary": ["BITCOIN ", " BTC "],
            "context": ["BLOCKCHAIN", "DIGITAL GOLD", "MINING", "HALVING", "BTC ETF", "SATOSHI", "CRYPTOCURRENCY"],
            "decoys": ["BTC.COM"]
        },
        "ETH": {
            "primary": ["ETHEREUM", " ETH "],
            "context": ["SMART CONTRACTS", "VITALIK", "STAKING", "LAYER 2", "GAS FEES", "ETH ETF"],
            "decoys": [" ETHICAL ", " ETHICS "]
        },
        "LINK": {
            "primary": ["CHAINLINK", " LINK "],
            "context": ["ORACLE", "WEB3", "SERGEY NAZAROV", "CCIP", "ABSTRACTION", "LINK TOKEN"],
            "decoys": ["HYPERLINK", "URL LINK", "DOWNLOAD LINK", "CLICK THE LINK"]
        },
        "AVAX": {
            "primary": ["AVALANCHE", " AVAX "],
            "context": ["CRYPTO", "SUBNET", "AVA LABS", "EMIN GUN SIRER", "BLIZZARD", "AVAX TOKEN"],
            "decoys": ["AVALANCHE WARNING", "SNOW AVALANCHE", "AVALANCHE RESCUE", "AVALANCHE DANGER"]
        }
    }

    best_ticker = "MIXED"
    max_score = 0

    for ticker, profile in PROFILES.items():
        score = 0
        # 1. Primary match (High weight)
        for term in profile["primary"]:
            if term in text:
                score += 10
        
        # 2. Context match (Medium weight)
        for term in profile["context"]:
            if term in text:
                score += 3
        
        # 3. Decoy detection (High penalty)
        for decoy in profile["decoys"]:
            if decoy in text:
                score -= 20
        
        if score > max_score:
            max_score = score
            best_ticker = ticker

    return best_ticker if max_score >= 8 else "MIXED"

def fetch_ticker_news(ticker):
    """Fetch RSS feed for a specific ticker from Yahoo Finance"""
    url = f"https://finance.yahoo.com/quote/{ticker}/rss"
    articles = []
    
    try:
        print(f"Fetching news for {ticker}...")
        feed = feedparser.parse(url, request_headers={'User-Agent': USER_AGENT})
        
        for entry in feed.entries:
            title = entry.get('title', '').strip()
            if not title: continue
                
            url_link = entry.get('link', '')
            description = entry.get('summary', '') or entry.get('description', '')
            if description:
                description = re.sub('<[^<]+?>', '', description)
                description = unescape(description).strip()
                
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
            else:
                published_at = datetime.now(timezone.utc).isoformat()
                
            article = {
                "id": str(uuid.uuid4()),
                "source": "yahoo_finance",
                "ticker": ticker.split('-')[0],
                "sentiment": get_simple_sentiment(title + " " + (description or "")),
                "title": title,
                "url": url_link,
                "description": description[:250] if description else None,
                "published_at": published_at,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "author": entry.get('author', 'Yahoo Finance'),
                "tags": [ticker, "Portfolio"],
                "image_url": None
            }
            articles.append(article)
    except Exception as e:
        log_error(f"Error fetching Yahoo news for {ticker}: {e}")
        
    return articles

def fetch_google_search_news():
    """
    Expert implementation of per-asset search with precision-oriented query engineering.
    """
    import urllib.parse
    
    # Precise query sets per asset
    ASSET_QUERIES = {
        "GOOG": '"Alphabet Inc" OR "GOOGL stock" OR "Google finance"',
        "EQIX": 'Equinix (stock OR REIT OR "data center")',
        "U": '"Unity Software" OR "Unity Technologies" OR "Unity stock"',
        "TDOC": '"Teladoc Health" OR "Teladoc stock"',
        "BTC": 'Bitcoin OR (BTC stock) OR "Bitcoin price"',
        "ETH": 'Ethereum OR (ETH crypto) OR "Ethereum price"',
        "LINK": '"Chainlink crypto" OR "LINK token"',
        "AVAX": '"Avalanche AVAX" OR "Avalanche crypto"'
    }
    
    finance_filter = 'stock OR shares OR earnings OR revenue OR "price" OR crypto'
    all_articles = []
    seen_urls = set()

    for asset, base_query in ASSET_QUERIES.items():
        query = f"({base_query}) AND ({finance_filter})"
        encoded_query = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            print(f"Retrieving high-precision Google News for {asset}...")
            feed = feedparser.parse(url, request_headers={'User-Agent': USER_AGENT})
            
            for entry in feed.entries:
                url_link = entry.get('link', '')
                if url_link in seen_urls: continue
                seen_urls.add(url_link)
                
                title = entry.get('title', '').strip()
                summary = entry.get('summary', '') or entry.get('description', '')
                if summary:
                    summary = re.sub('<[^<]+?>', '', summary)
                    summary = unescape(summary).strip()
                
                # Dynamic matching and ranking
                matched_ticker = assign_ticker(title, summary or "")
                # Force match the searched asset if it was high precision and didn't trigger decoys
                if matched_ticker == "MIXED" and asset in (title + (summary or "")).upper():
                    matched_ticker = asset
                
                if matched_ticker == "MIXED": continue # Drop low relevance

                published_at = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
                else:
                    published_at = datetime.now(timezone.utc).isoformat()

                article = {
                    "id": str(uuid.uuid4()),
                    "source": "google_finance",
                    "ticker": matched_ticker,
                    "sentiment": get_simple_sentiment(title + " " + (summary or "")),
                    "title": title,
                    "url": url_link,
                    "description": summary[:250] if summary else None,
                    "published_at": published_at,
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "author": entry.get('source', {}).get('title', 'Google News'),
                    "tags": [matched_ticker, "Portfolio Search"],
                    "image_url": None
                }
                all_articles.append(article)
        except Exception as e:
            log_error(f"Error fetching Google News for {asset}: {e}")
            
    return all_articles

def main():
    print("=" * 60)
    print("AI Portfolio Search Engineer - Scraper")
    print("=" * 60)
    
    all_articles = []
    
    # 1. Yahoo Finance Ticker Feeds
    for ticker in TICKERS:
        all_articles.extend(fetch_ticker_news(ticker))
        
    # 2. Precision Google News Searches
    all_articles.extend(fetch_google_search_news())
    
    # 3. Generate AI Analysis per Ticker
    try:
        from tools.generate_ai_analysis import generate_ai_analysis
    except ImportError:
        from generate_ai_analysis import generate_ai_analysis
    
    ticker_analyses = {}
    tickers_to_parse = ["GOOG", "EQIX", "U", "TDOC", "BTC", "ETH", "LINK", "AVAX"]
    
    import time
    for i, ticker_symbol in enumerate(tickers_to_parse):
        # Get headlines for this ticker to use as context
        headlines = [a["title"] for a in all_articles if a["ticker"] == ticker_symbol][:5]
        news_context = "\n".join(headlines)
        
        print(f"Generating AI Intelligence for {ticker_symbol} ({i+1}/{len(tickers_to_parse)})...")
        analysis = generate_ai_analysis(ticker_symbol, news_context)
        ticker_analyses[ticker_symbol] = analysis
        
        # Space out requests to avoid 429 quota errors on free tier
        if i < len(tickers_to_parse) - 1:
            print("Quota management: waiting 4s...")
            time.sleep(4)

    # Save raw results with AI analyses
    payload = {
        "articles": all_articles,
        "analyses": ticker_analyses,
        "last_updated": datetime.now(timezone.utc).isoformat()
    }
    
    os.makedirs(os.path.dirname(RAW_OUTPUT), exist_ok=True)
    with open(RAW_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Successfully scraped {len(all_articles)} articles + generated {len(ticker_analyses)} AI analyses")
    sys.exit(0)

if __name__ == "__main__":
    main()
