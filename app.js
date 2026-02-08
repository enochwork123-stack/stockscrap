/**
 * glaid AI News Dashboard
 * Main Application Logic
 */

// ============================================
// State Management
// ============================================

const AppState = {
    articles: [],
    savedArticles: new Set(),
    currentFilter: 'all',
    metadata: null
};

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
        const saved = localStorage.getItem('glaid_saved_articles');
        if (saved) {
            AppState.savedArticles = new Set(JSON.parse(saved));
        }
    } catch (error) {
        console.error('Error loading saved articles:', error);
    }
}

function saveSavedArticles() {
    try {
        localStorage.setItem('glaid_saved_articles', JSON.stringify([...AppState.savedArticles]));
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
    card.setAttribute('data-article-id', article.id);

    const isSaved = AppState.savedArticles.has(article.id);
    const sourceLabel = formatSourceLabel(article.source, article);
    const relativeTime = formatRelativeTime(article.published_at);

    card.innerHTML = `
        <div class="article-header">
            <span class="article-source ${article.source}">${sourceLabel}</span>
            <button class="save-btn ${isSaved ? 'saved' : ''}" data-article-id="${article.id}">
                ${isSaved ? '⭐' : '☆'}
            </button>
        </div>
        <h3 class="article-title">${escapeHtml(article.title)}</h3>
        ${article.description ? `<p class="article-description">${escapeHtml(article.description)}</p>` : ''}
        <div class="article-meta">
            <span class="article-author">${escapeHtml(article.author || 'Unknown')}</span>
            <span class="article-date">${relativeTime}</span>
        </div>
    `;

    // Add click handler to open article
    card.addEventListener('click', (e) => {
        if (!e.target.classList.contains('save-btn')) {
            window.open(article.url, '_blank');
        }
    });

    // Add save button handler
    const saveBtn = card.querySelector('.save-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleSaveArticle(article.id);
        });
    }

    return card;
}

// ============================================
// User Interactions
// ============================================

function toggleSaveArticle(articleId) {
    if (AppState.savedArticles.has(articleId)) {
        AppState.savedArticles.delete(articleId);
    } else {
        AppState.savedArticles.add(articleId);
    }

    saveSavedArticles();
    renderStats();

    // Update the button
    const btn = document.querySelector(`.save-btn[data-article-id="${articleId}"]`);
    if (btn) {
        const isSaved = AppState.savedArticles.has(articleId);
        btn.textContent = isSaved ? '⭐' : '☆';
        btn.classList.toggle('saved', isSaved);
    }
}

function setFilter(filter) {
    AppState.currentFilter = filter;

    // Update active tab
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.filter === filter);
    });

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
    console.log('🚀 glaid AI News Dashboard initialized');
    initEventListeners();
    loadDashboardData();
});
