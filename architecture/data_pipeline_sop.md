# Data Pipeline Architecture SOP

## Purpose
Define how scraped data flows from raw HTML to the dashboard display.

## Pipeline Stages

### Stage 1: Scraping (Tools Layer)
- **Input:** Website URLs
- **Process:** `scrape_bens_bites.py`, `scrape_ai_rundown.py`
- **Output:** Raw JSON arrays of articles
- **Storage:** `.tmp/raw_bens_bites.json`, `.tmp/raw_ai_rundown.json`

### Stage 2: Filtering (Tools Layer)
- **Input:** Raw JSON arrays
- **Process:** `filter_24h_articles.py`
- **Logic:** Filter articles where `published_at` is within last 24 hours
- **Output:** Filtered JSON arrays
- **Storage:** `.tmp/filtered_articles.json`

### Stage 3: Deduplication (Tools Layer)
- **Input:** Filtered JSON arrays
- **Process:** `deduplicate_articles.py`
- **Logic:** Remove duplicate articles based on URL
- **Output:** Deduplicated JSON array
- **Storage:** `.tmp/deduplicated_articles.json`

### Stage 4: Aggregation (Navigation Layer)
- **Input:** Deduplicated articles from all sources
- **Process:** Combine into single payload
- **Output:** Dashboard payload matching Output Schema
- **Storage:** `.tmp/dashboard_payload.json`

### Stage 5: Display (Dashboard)
- **Input:** Dashboard payload JSON
- **Process:** JavaScript reads JSON and renders article cards
- **Output:** Beautiful UI with article cards
- **Storage:** Browser localStorage for saved articles

## Data Flow Diagram
```
[Ben's Bites] → scrape_bens_bites.py → raw_bens_bites.json
                                              ↓
[AI Rundown] → scrape_ai_rundown.py → raw_ai_rundown.json
                                              ↓
                                    filter_24h_articles.py
                                              ↓
                                    filtered_articles.json
                                              ↓
                                    deduplicate_articles.py
                                              ↓
                                    deduplicated_articles.json
                                              ↓
                                    [Aggregation Logic]
                                              ↓
                                    dashboard_payload.json
                                              ↓
                                    [Dashboard UI] → localStorage
```

## File Locations
- **Raw scraped data:** `.tmp/raw_*.json`
- **Processed data:** `.tmp/filtered_*.json`, `.tmp/deduplicated_*.json`
- **Final payload:** `.tmp/dashboard_payload.json`
- **Error logs:** `.tmp/scraper_errors.log`
- **Saved articles:** Browser localStorage (key: `glaid_saved_articles`)

## Execution Order
1. Run `scrape_bens_bites.py` (parallel)
2. Run `scrape_ai_rundown.py` (parallel)
3. Run `filter_24h_articles.py` (sequential, after scrapers)
4. Run `deduplicate_articles.py` (sequential, after filtering)
5. Generate dashboard payload (sequential, after deduplication)
6. Dashboard reads payload and renders UI

## Automation (Phase 5)
- **Trigger:** Cron job every 24 hours
- **Script:** `run_pipeline.sh` (orchestrates all tools)
- **Notification:** Log to Supabase or send alert if errors

## Error Recovery
- If scraper fails: Use cached data from previous run
- If filtering fails: Display all articles (no time filter)
- If deduplication fails: Display with duplicates (non-critical)
- Always log errors for debugging

## Performance Considerations
- Scrapers run in parallel (faster)
- Cache raw HTML for 24 hours (avoid re-scraping)
- Deduplicate early to reduce processing
- Minimize file I/O operations

## Maintenance
- Monitor `.tmp/` directory size
- Clean up old files after 7 days
- Update this SOP when pipeline changes
