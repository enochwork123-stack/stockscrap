#!/usr/bin/env python3
"""
Deduplicate Articles
Removes duplicate articles based on URL
"""

import json
import sys
import os

INPUT_FILE = ".tmp/filtered_articles.json"
OUTPUT_FILE = "data/dashboard_payload.js"

def load_articles():
    """Load filtered articles"""
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading articles: {e}", file=sys.stderr)
        return []

def deduplicate(articles):
    """Remove duplicates based on URL"""
    seen_urls = set()
    unique = []
    
    for article in articles:
        url = article.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(article)
    
    return unique

def create_payload(articles):
    """Create dashboard payload with metadata"""
    from datetime import datetime, timezone
    
    # Count by source
    sources_count = {
        "bens_bites": 0,
        "ai_rundown": 0,
        "yahoo_finance": 0,
        "google_finance": 0,
        "reddit": 0
    }
    
    for article in articles:
        source = article.get('source', '')
        if source in sources_count:
            sources_count[source] += 1
    
    payload = {
        "articles": articles,
        "metadata": {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "total_articles": len(articles),
            "sources_count": sources_count
        },
        "saved_articles": []
    }
    
    return payload

def save_payload(payload):
    """Save dashboard payload as a JS variable assignment"""
    try:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("window.DASHBOARD_DATA = ")
            json.dump(payload, f, indent=2, ensure_ascii=False)
            f.write(";")
        print(f"Saved dashboard payload to {OUTPUT_FILE}")
        return True
    except Exception as e:
        print(f"Error saving payload: {e}", file=sys.stderr)
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("Article Deduplication & Payload Generation")
    print("=" * 60)
    
    # Load articles
    articles = load_articles()
    print(f"Loaded {len(articles)} filtered articles")
    
    # Deduplicate
    unique = deduplicate(articles)
    print(f"Unique articles: {len(unique)}")
    
    # Create payload
    payload = create_payload(unique)
    
    # Save
    if save_payload(payload):
        print(f"✅ Successfully created dashboard payload")
        print(f"   Total: {payload['metadata']['total_articles']} articles")
        print(f"   Ben's Bites: {payload['metadata']['sources_count']['bens_bites']}")
        print(f"   AI Rundown: {payload['metadata']['sources_count']['ai_rundown']}")
        sys.exit(0)
    else:
        print("Failed to save payload")
        sys.exit(1)

if __name__ == "__main__":
    main()
