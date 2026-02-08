#!/bin/bash
# glaid AI News Dashboard - Update Script
# This script runs the complete data pipeline

echo "============================================"
echo "glaid AI News Dashboard - Data Update"
echo "============================================"
echo ""

#📰 Step 0: Scraping Portfolio News...
echo "📰 Step 0: Scraping Portfolio News (GOOG, EQIX, U, TDOC, BTC)..."
python3 tools/scrape_portfolio.py
echo ""

# Step 1: Scrape Ben's Bites
echo "📰 Step 1: Scraping Ben's Bites..."
python3 tools/scrape_bens_bites.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to scrape Ben's Bites"
    exit 1
fi
echo ""

# Step 2: Scrape AI Rundown (optional - may fail)
echo "📰 Step 2: Scraping AI Rundown..."
python3 tools/scrape_ai_rundown.py
# Don't exit on failure - AI Rundown is optional
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
