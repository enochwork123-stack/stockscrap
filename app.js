/**
 * Enozil AI News Dashboard
 * Main Application Logic
 */

// ============================================
// State Management
// ============================================

const AppState = {
    articles: [],
    savedArticles: new Set(),
    currentFilter: 'all',
    metadata: null,
    tvWidget: null
};

// ============================================
// TradingView Chart Configuration
// ============================================

// Map from filter tab name → TradingView symbol
const TICKER_TV_SYMBOLS = {
    'google': 'NASDAQ:GOOGL',
    'eqix': 'NASDAQ:EQIX',
    'u': 'NYSE:U',
    'tdoc': 'NYSE:TDOC',
    'btc': 'BINANCE:BTCUSDT',
    'eth': 'BINANCE:ETHUSDT',
    'link': 'BINANCE:LINKUSDT',
    'avax': 'BINANCE:AVAXUSDT'
};

const TICKER_DISPLAY_NAMES = {
    'google': 'Alphabet (GOOGL)',
    'eqix': 'Equinix (EQIX)',
    'u': 'Unity Software (U)',
    'tdoc': 'Teladoc Health (TDOC)',
    'btc': 'Bitcoin (BTC/USDT)',
    'eth': 'Ethereum (ETH/USDT)',
    'link': 'Chainlink (LINK/USDT)',
    'avax': 'Avalanche (AVAX/USDT)'
};

function renderChart(filter) {
    const symbol = TICKER_TV_SYMBOLS[filter];
    const chartSection = document.getElementById('chartSection');
    const chartTitle = document.getElementById('chartTitle');
    const chartContainer = document.getElementById('tradingview_chart');

    if (!symbol || !chartSection) return;

    // Show section
    chartSection.style.display = 'block';
    if (chartTitle) chartTitle.textContent = (TICKER_DISPLAY_NAMES[filter] || filter.toUpperCase()) + ' — Price Chart';

    // Clear previous widget
    chartContainer.innerHTML = '';

    // Create TradingView Advanced Chart widget
    // Use explicit height so sub-indicator panes (RSI, MACD, BB, DMI) all get rendered
    new TradingView.widget({
        container_id: 'tradingview_chart',
        width: '100%',
        height: 900,
        symbol: symbol,
        interval: 'D',          // Daily candles
        timezone: 'exchange',
        theme: 'dark',
        style: '1',             // Candlestick
        locale: 'en',
        toolbar_bg: '#0d1117',
        enable_publishing: false,
        hide_top_toolbar: false,
        hide_legend: false,
        save_image: true,
        withdateranges: true,
        allow_symbol_change: true,
        studies: [
            'RSI@tv-basicstudies',
            'MACD@tv-basicstudies',
            'BB@tv-basicstudies'
        ],
        show_popup_button: true,
        popup_width: '1200',
        popup_height: '800',
        no_referral_id: true
    });
}

function hideChart() {
    const chartSection = document.getElementById('chartSection');
    if (chartSection) chartSection.style.display = 'none';
    const chartContainer = document.getElementById('tradingview_chart');
    if (chartContainer) chartContainer.innerHTML = '';
}

// ============================================
// Data Loading
// ============================================

async function loadDashboardData() {
    try {
        // Use global variable from dashboard_payload.js to bypass CORS
        if (!window.DASHBOARD_DATA) {
            throw new Error('Dashboard data not found. Please run the update script.');
        }

        const data = window.DASHBOARD_DATA;
        AppState.articles = data.articles || [];
        AppState.metadata = data.metadata || {};

        // Load saved articles from localStorage
        loadSavedArticles();

        // Render UI
        renderStats();
        renderArticles();

    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showError(error.message || 'Failed to load articles. Please refresh the page.');
    }
}

function loadSavedArticles() {
    try {
        const saved = localStorage.getItem('enozil_saved_articles') || localStorage.getItem('glaid_saved_articles');
        if (saved) {
            AppState.savedArticles = new Set(JSON.parse(saved));
        }
    } catch (error) {
        console.error('Error loading saved articles:', error);
    }
}

function saveSavedArticles() {
    try {
        localStorage.setItem('enozil_saved_articles', JSON.stringify([...AppState.savedArticles]));
    } catch (error) {
        console.error('Error saving articles:', error);
    }
}

// ============================================
// UI Rendering
// ============================================

function renderStats() {
    const totalArticlesEl = document.getElementById('totalArticles');
    const savedArticlesEl = document.getElementById('savedArticles');
    const lastUpdatedEl = document.getElementById('lastUpdated');

    if (totalArticlesEl) {
        totalArticlesEl.textContent = AppState.articles.length;
    }

    if (savedArticlesEl) {
        savedArticlesEl.textContent = AppState.savedArticles.size;
    }

    if (lastUpdatedEl && AppState.metadata?.last_updated) {
        lastUpdatedEl.textContent = formatRelativeTime(AppState.metadata.last_updated);
    }
}

function renderArticles() {
    const grid = document.getElementById('articlesGrid');
    const emptyState = document.getElementById('emptyState');

    if (!grid) return;

    // Clear grid
    grid.innerHTML = '';

    // Filter articles
    const filteredArticles = AppState.articles.filter(article => {
        if (AppState.currentFilter === 'all') return true;
        if (AppState.currentFilter === 'saved') return AppState.savedArticles.has(article.id);

        // Handle ticker filtering
        const tickerFilter = AppState.currentFilter.toLowerCase();
        const articleTicker = (article.ticker || '').toLowerCase();

        if (['google', 'eqix', 'u', 'tdoc', 'btc', 'eth', 'link', 'avax'].includes(tickerFilter)) {
            // Special case for 'google' matching 'goog'
            if (tickerFilter === 'google' && articleTicker.includes('goog')) return true;
            return articleTicker.includes(tickerFilter);
        }

        return article.source === AppState.currentFilter;
    });

    if (filteredArticles.length === 0) {
        grid.style.display = 'none';
        if (emptyState) emptyState.style.display = 'block';
        return;
    }

    grid.style.display = 'grid';
    if (emptyState) emptyState.style.display = 'none';

    // Render each article
    filteredArticles.forEach(article => {
        const card = createArticleCard(article);
        grid.appendChild(card);
    });
}

function getFilteredArticles() {
    const filter = AppState.currentFilter;

    if (filter === 'all') {
        return AppState.articles;
    } else if (filter === 'saved') {
        return AppState.articles.filter(article => AppState.savedArticles.has(article.id));
    } else {
        return AppState.articles.filter(article => article.source === filter);
    }
}

function createArticleCard(article) {
    const card = document.createElement('div');
    card.className = 'article-card';
    card.id = `article-${article.id}`;

    const sourceLabel = formatSourceLabel(article.source, article);
    const tickerClass = (article.ticker || 'unknown').toLowerCase();
    const sentiment = article.sentiment || 'neutral';

    card.innerHTML = `
        <div class="article-meta">
            <span class="source-badge ${tickerClass}">${sourceLabel}</span>
            <span class="sentiment-badge ${sentiment}">${sentiment}</span>
        </div>
        <h3 class="article-title">
            <a href="${article.url}" target="_blank">${article.title}</a>
        </h3>
        <p class="article-description">${article.description || 'No description available.'}</p>
        <div class="article-footer">
            <span class="article-date">${formatRelativeTime(article.published_at)}</span>
            <div class="article-actions">
                <button class="save-btn ${AppState.savedArticles.has(article.id) ? 'active' : ''}" 
                        title="Save article">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                    </svg>
                </button>
            </div>
        </div>
    `;

    // Click handler to open article (on card click)
    card.addEventListener('click', (e) => {
        if (!e.target.closest('.save-btn')) {
            window.open(article.url, '_blank');
        }
    });

    // Save button handler
    const saveBtn = card.querySelector('.save-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleSaveArticle(article.id, saveBtn);
        });
    }

    return card;
}

// ============================================
// User Interactions
// ============================================

function toggleSaveArticle(articleId, btnEl) {
    const isSaved = AppState.savedArticles.has(articleId);

    if (isSaved) {
        AppState.savedArticles.delete(articleId);
        if (btnEl) btnEl.classList.remove('active');
    } else {
        AppState.savedArticles.add(articleId);
        if (btnEl) btnEl.classList.add('active');
    }

    saveSavedArticles();
    renderStats();

    // If we are in the 'saved' tab, re-render to remove the article
    if (AppState.currentFilter === 'saved') {
        renderArticles();
    }
}

function setFilter(filter) {
    AppState.currentFilter = filter;

    // Update active tab
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.filter === filter);
    });

    // Show/hide chart
    if (TICKER_TV_SYMBOLS[filter]) {
        renderChart(filter);
    } else {
        hideChart();
    }

    // Re-render articles
    renderArticles();
}

async function refreshData() {
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 8C14 11.3137 11.3137 14 8 14C4.68629 14 2 11.3137 2 8C2 4.68629 4.68629 2 8 2C9.84 2 11.4667 2.84 12.5333 4.13333" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                <path d="M14 4V4.13333C14 4.13333 14 6 14 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 4H14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Refreshing...
        `;
    }

    await loadDashboardData();

    if (refreshBtn) {
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 8C14 11.3137 11.3137 14 8 14C4.68629 14 2 11.3137 2 8C2 4.68629 4.68629 2 8 2C9.84 2 11.4667 2.84 12.5333 4.13333" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                <path d="M14 4V4.13333C14 4.13333 14 6 14 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 4H14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Refresh
        `;
    }
}

// ============================================
// Utility Functions
// ============================================

function formatSourceLabel(source, article = null) {
    if (article && article.ticker && article.ticker !== 'PORTFOLIO') {
        return article.ticker;
    }
    const labels = {
        'bens_bites': "Ben's Bites",
        'ai_rundown': 'AI Rundown',
        'yahoo_finance': 'Yahoo Finance',
        'google_finance': 'Google Finance',
        'reddit': 'Reddit'
    };
    return labels[source] || source;
}

function formatRelativeTime(dateString) {
    try {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;

        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } catch (error) {
        return 'Recently';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    const grid = document.getElementById('articlesGrid');
    if (grid) {
        grid.innerHTML = `
            <div class="empty-state" style="display: block;">
                <div class="empty-icon">⚠️</div>
                <h3>Error</h3>
                <p>${escapeHtml(message)}</p>
            </div>
        `;
    }
}

// ============================================
// Event Listeners
// ============================================

function initEventListeners() {
    // Filter tabs
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            setFilter(tab.dataset.filter);
        });
    });

    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshData);
    }
}

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Enozil AI News Dashboard initialized');
    initEventListeners();
    loadDashboardData();
});
