# glaid - Financial News & Portfolio Dashboard

<div align="center">
  <img src="DesignGuidelines/Logo.png" alt="glaid logo" width="120">
  <h3>Your Premium Financial News Aggregator</h3>
  <p>Track your portfolio and stay updated with the latest market developments for GOOG, EQIX, U, TDOC, & BTC.</p>
</div>

---

## ✨ Features

- 🎨 **Premium Design** - Beautiful glassmorphism UI with glaid branding
- 💹 **Portfolio Focused** - Strictly monitors news for: **Google (GOOG), Equinix (EQIX), Unity (U), Teladoc (TDOC), and Bitcoin (BTC)**
- ⭐ **Save Articles** - Bookmark your favorite articles with localStorage persistence
- 🔍 **Smart Ticker Filtering** - Dedicated tabs to drill down into specific assets in your portfolio
- 🏷️ **Automatic Tagging** - AI-driven tagging system that identifies tickers within general financial news
- 📱 **Responsive** - Works beautifully on desktop, tablet, and mobile
- 🚀 **Fast & Lightweight** - Vanilla JavaScript, no frameworks needed

## 🏗️ Architecture

The project follows the **A.N.T. 3-Layer Architecture**:

### Layer 1: Architecture (SOPs)
- `architecture/scraper_sop.md` - Web scraping guidelines
- `architecture/data_pipeline_sop.md` - Data flow specifications
- `architecture/dashboard_sop.md` - UI/UX specifications

### Layer 2: Tools (Executables)
- `tools/scrape_portfolio.py` - targeted Portfolio news scraper (Google & Yahoo News)
- `tools/scrape_yahoo_finance.py` - Yahoo Finance RSS scraper
- `tools/scrape_google_finance.py` - Google Finance RSS scraper
- `tools/filter_24h_articles.py` - Date-based article filter & ticker tagging
- `tools/deduplicate_articles.py` - Deduplication & payload generator

### Layer 3: Touchpoints (UI)
- `index.html` - Main portfolio dashboard
- `styles.css` - Design system & ticker-specific styling
- `app.js` - Application logic & filtering

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Modern web browser

### Installation

1. **Install Python dependencies:**
```bash
pip3 install -r requirements.txt
```

2. **Run the data pipeline:**
```bash
./update_dashboard.sh
```

3. **Open the dashboard:**
```bash
open index.html
```

## 📖 Usage

### Updating the Dashboard

Run the update script to fetch the latest articles:

```bash
./update_dashboard.sh
```

This will:
1. Scrape targeted news for your portfolio (GOOG, EQIX, U, TDOC, BTC)
2. Scrape general market news from Yahoo & Google Finance
3. Filter articles from the last 7 days matched against your portfolio
4. Automatically tag articles with ticker symbols
5. Generate the dashboard payload

### Dashboard Features

- **Filter by Asset**: Click tabs (Google, Bitcoin, etc.) to see news for specific holdings
- **Save Articles**: Click the ⭐ icon to save articles (persists in localStorage)
- **View Saved**: Click "Saved" tab to see your bookmarked articles
- **Refresh**: Click the refresh button to reload the data
- **Read Article**: Click anywhere on a card to open the article in a new tab

## 📁 Project Structure

```
Trial/
├── index.html                 # Main dashboard page
├── styles.css                 # Design system & styling
├── app.js                     # Application logic
├── update_dashboard.sh        # Master update script
├── requirements.txt           # Python dependencies
│
├── architecture/              # Layer 1: SOPs
│   ├── scraper_sop.md
│   ├── data_pipeline_sop.md
│   └── dashboard_sop.md
│
├── tools/                     # Layer 2: Executables
│   ├── scrape_portfolio.py    # Targeted portfolio news
│   ├── scrape_yahoo_finance.py
│   ├── scrape_google_finance.py
│   ├── filter_24h_articles.py
│   └── deduplicate_articles.py
│
├── .tmp/                      # Data files (auto-generated)
│   ├── raw_portfolio.json
│   ├── dashboard_payload.js   # Main data payload
│
├── DesignGuidelines/          # Brand assets
│   ├── Logo.png
│   └── BrandDesign
```

## 🛠️ Development

### Tech Stack
- **Backend**: Python 3, feedparser, requests
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Data Format**: JSON/JS (bypasses CORS for local execution)
- **Persistence**: localStorage

## 🚧 Roadmap

- [ ] Implement Supabase backend
- [ ] Add real-time stock price integration
- [ ] Add daily automated scraping (cron job)
- [ ] Add search functionality
- [ ] Add dark/light mode toggle

## 📝 License

© 2026 glaid. All rights reserved.

---

<div align="center">
  <p>Built with ❤️ using the A.N.T. Architecture</p>
  <p><strong>Powered by AI</strong></p>
</div>
