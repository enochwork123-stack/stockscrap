# Scraper Architecture SOP

## Purpose
Define the technical approach for scraping AI news articles from Ben's Bites and AI Rundown websites.

## Goals
1. Extract article data (title, URL, description, published date) from target websites
2. Filter articles to only include those from the last 24 hours
3. Transform raw HTML into structured JSON matching our data schema
4. Handle errors gracefully and log all activities
5. Respect website terms of service and rate limits

## Input
- **Target URLs:**
  - Ben's Bites: `https://bensbites.com`
  - AI Rundown: `https://www.therundown.ai`

## Output
- **JSON Array** of articles matching the Input Schema defined in `gemini.md`:
```json
{
  "id": "UUID",
  "source": "bens_bites" | "ai_rundown",
  "title": "string",
  "url": "string",
  "description": "string",
  "published_at": "ISO 8601 timestamp",
  "scraped_at": "ISO 8601 timestamp",
  "content_preview": "string (optional)",
  "author": "string (optional)",
  "tags": ["string"] (optional),
  "image_url": "string (optional)"
}
```

## Technology Stack
- **Python 3.x**
- **requests** - HTTP client for fetching HTML
- **BeautifulSoup4** - HTML parsing
- **datetime** - Timestamp handling and 24-hour filtering
- **uuid** - Generate unique IDs
- **json** - Data serialization

## Scraping Logic

### Ben's Bites (bensbites.com)
1. Fetch homepage HTML
2. Parse with BeautifulSoup
3. Find article links (likely in `<a>` tags with specific classes)
4. Extract:
   - Title (from link text or heading)
   - URL (from href attribute)
   - Description (from subtitle or preview text)
   - Published date (from time element or metadata)
5. Filter to last 24 hours
6. Transform to JSON schema

### AI Rundown (therundown.ai)
1. Fetch homepage HTML
2. Parse with BeautifulSoup
3. Find "Latest Articles" section
4. Extract H3 headers as titles
5. Extract article links
6. Extract "PLUS:" descriptions
7. Extract published dates
8. Filter to last 24 hours
9. Transform to JSON schema

## Best Practices
1. **User-Agent:** Use realistic browser User-Agent header
2. **Rate Limiting:** Add 1-2 second delay between requests
3. **Error Handling:** Try/except blocks with detailed logging
4. **Caching:** Save raw HTML to `.tmp/` for debugging
5. **Logging:** Log all scraping activities with timestamps
6. **Validation:** Verify extracted data matches schema before returning

## Edge Cases
1. **No articles found:** Return empty array, log warning
2. **Network error:** Retry up to 3 times with exponential backoff
3. **Parsing error:** Log error with HTML snippet, continue with other articles
4. **Missing fields:** Use None/null for optional fields, skip article if required field missing
5. **Date parsing failure:** Skip article if can't determine publish date
6. **Duplicate URLs:** Deduplicate based on URL

## Error Handling
- Network errors: Retry with backoff
- Parsing errors: Log and skip individual article
- Schema validation errors: Log and skip article
- All errors logged to `.tmp/scraper_errors.log`

## Testing
1. Test each scraper independently
2. Verify output matches JSON schema
3. Test 24-hour filtering logic
4. Test error handling (mock network failures)
5. Verify rate limiting works

## Maintenance Notes
- Website structures may change - update selectors as needed
- Monitor error logs for parsing failures
- Update this SOP when logic changes
