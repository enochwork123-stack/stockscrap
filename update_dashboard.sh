#!/bin/bash
# glaid AI News Dashboard - Update Script
# This script runs the complete data pipeline

echo "============================================"
echo "glaid AI News Dashboard - Data Update"
echo "============================================"
echo ""

#📰 Step 0: Scraping Portfolio News (GOOG, EQIX, U, TDOC, BTC, ETH, LINK, AVAX)...
echo "📰 Step 0: Scraping Portfolio News..."
python3 tools/scrape_portfolio.py
echo ""

# Step 1: Scrape Financial RSS (Bloomberg & Reuters)
echo "📰 Step 1: Scraping Financial News (Bloomberg & Reuters)..."
python3 tools/scrape_financial_rss.py
echo ""

# Step 2: Scrape Crypto RSS (CoinDesk & The Block)
echo "📰 Step 2: Scraping Crypto News (CoinDesk & The Block)..."
python3 tools/scrape_crypto_rss.py
echo ""

# Step 2a: Scrape Yahoo Finance
echo "📰 Step 2a: Scraping Yahoo Finance..."
python3 tools/scrape_yahoo_finance.py
echo ""

# Step 2b: Scrape Google Finance
echo "📰 Step 2b: Scraping Google Finance..."
python3 tools/scrape_google_finance.py
echo ""

# Step 3: Filter articles (last 7 days)
echo "🔍 Step 3: Filtering articles..."
python3 tools/filter_24h_articles.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to filter articles"
    exit 1
fi
echo ""

# Step 4: Deduplicate and create payload
echo "🎯 Step 4: Creating dashboard payload..."
python3 tools/deduplicate_articles.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to create payload"
    exit 1
fi
echo ""

echo "============================================"
echo "✅ Dashboard data updated successfully!"
echo "============================================"
echo ""
echo "Open index.html in your browser to view the dashboard"
echo "Or run: open index.html"
