# Dashboard Architecture SOP

## Purpose
Define the technical approach for building the glaid AI News Dashboard UI.

## Goals
1. Display latest AI news articles in a beautiful, card-based layout
2. Allow users to save/unsave articles with persistence
3. Filter articles by source
4. Show metadata (article count, last updated, source distribution)
5. Provide premium, professional user experience

## Technology Stack
- **HTML5** - Semantic structure
- **CSS3** - Styling with glaid brand design
- **Vanilla JavaScript** - Interactivity and data handling
- **localStorage** - Save article persistence (Phase 1)
- **Supabase** - Database persistence (Phase 5)

## File Structure
```
/dashboard/
  ├── index.html          # Main dashboard page
  ├── css/
  │   ├── reset.css       # CSS reset
  │   ├── variables.css   # Design tokens (colors, spacing)
  │   ├── components.css  # Reusable components
  │   └── main.css        # Layout and page styles
  ├── js/
  │   ├── config.js       # Configuration
  │   ├── data.js         # Data fetching and management
  │   ├── ui.js           # UI rendering
  │   └── main.js         # App initialization
  └── assets/
      ├── logo.png        # glaid logo
      └── icons/          # SVG icons
```

## Design System Implementation

### CSS Variables (variables.css)
```css
:root {
  /* Brand Colors */
  --color-primary: #FF6B4A;
  --color-primary-light: #FFB8A8;
  --color-dark: #2D2D2D;
  --color-white: #FFFFFF;
  --color-gray-light: #F5F5F5;
  --color-gray: #9CA3AF;
  
  /* Semantic Colors */
  --color-success: #10B981;
  --color-warning: #EF4444;
  
  /* Typography */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-size-h1: 32px;
  --font-size-h2: 24px;
  --font-size-body: 16px;
  --font-size-small: 14px;
  --font-size-tiny: 12px;
  
  /* Spacing */
  --spacing-xs: 8px;
  --spacing-sm: 12px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* Border Radius */
  --radius-sm: 8px;
  --radius-md: 12px;
  
  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  
  /* Transitions */
  --transition-fast: 200ms ease;
  --transition-normal: 300ms ease;
}
```

### Component: Article Card
**HTML Structure:**
```html
<article class="article-card" data-article-id="{id}">
  <div class="article-header">
    <span class="source-badge">{source}</span>
    <button class="save-btn" aria-label="Save article">
      <svg><!-- heart icon --></svg>
    </button>
  </div>
  <h3 class="article-title">{title}</h3>
  <p class="article-description">{description}</p>
  <div class="article-footer">
    <time class="article-time">{published_at}</time>
    <a href="{url}" class="article-link" target="_blank">Read more →</a>
  </div>
</article>
```

**CSS Styling:**
- White background with `--shadow-md`
- Border radius `--radius-md`
- Padding `--spacing-lg`
- Hover: Scale 1.02, increase shadow
- Transition: `--transition-normal`

### Component: Source Badge
- Background: `--color-primary` for active source
- Background: `--color-gray-light` for inactive
- Border radius: `--radius-sm`
- Padding: `--spacing-xs` `--spacing-sm`
- Font size: `--font-size-tiny`
- Font weight: 500

### Layout
**Grid System:**
- Desktop (>1200px): 3 columns
- Tablet (768px-1199px): 2 columns
- Mobile (<768px): 1 column
- Gap: `--spacing-lg`

**Header:**
- glaid logo (left)
- Last updated timestamp (right)
- Background: `--color-white`
- Border bottom: 1px solid `--color-gray-light`

**Filters Section:**
- Source filter pills (All, Ben's Bites, AI Rundown)
- Active state: `--color-primary` background
- Inactive state: `--color-gray-light` background

**Stats Section:**
- Total articles count
- Articles per source
- Last updated time
- Display in clean, minimal cards

## JavaScript Logic

### Data Management (data.js)
```javascript
// Fetch dashboard payload
async function fetchArticles() {
  const response = await fetch('/.tmp/dashboard_payload.json');
  return await response.json();
}

// Get saved articles from localStorage
function getSavedArticles() {
  return JSON.parse(localStorage.getItem('glaid_saved_articles') || '[]');
}

// Save article
function saveArticle(articleId) {
  const saved = getSavedArticles();
  if (!saved.includes(articleId)) {
    saved.push(articleId);
    localStorage.setItem('glaid_saved_articles', JSON.stringify(saved));
  }
}

// Unsave article
function unsaveArticle(articleId) {
  const saved = getSavedArticles();
  const filtered = saved.filter(id => id !== articleId);
  localStorage.setItem('glaid_saved_articles', JSON.stringify(filtered));
}
```

### UI Rendering (ui.js)
```javascript
// Render article cards
function renderArticles(articles, savedArticles) {
  const container = document.getElementById('articles-grid');
  container.innerHTML = articles.map(article => 
    createArticleCard(article, savedArticles.includes(article.id))
  ).join('');
}

// Create article card HTML
function createArticleCard(article, isSaved) {
  // Return HTML string for article card
}

// Update stats
function updateStats(metadata) {
  // Update total count, source counts, last updated
}
```

### Interactivity (main.js)
- Load articles on page load
- Handle save/unsave button clicks
- Handle source filter clicks
- Handle refresh button click
- Add smooth scroll animations
- Add loading states

## User Interactions

### Save Article
1. User clicks heart icon
2. Add article ID to localStorage
3. Update UI (fill heart icon with orange)
4. Show subtle success animation

### Filter by Source
1. User clicks source filter pill
2. Filter articles array by source
3. Re-render article grid
4. Update active filter state

### Refresh Data
1. User clicks refresh button
2. Show loading skeleton
3. Re-fetch dashboard payload
4. Re-render articles
5. Update last updated timestamp

## Performance Optimizations
- Lazy load images (if added)
- Debounce filter interactions
- Use CSS transforms for animations (GPU-accelerated)
- Minimize DOM manipulations
- Cache DOM queries

## Accessibility
- Semantic HTML5 elements
- ARIA labels on interactive elements
- Keyboard navigation support
- Focus visible states
- Alt text for images

## Responsive Design
- Mobile-first approach
- Flexible grid layout
- Touch-friendly button sizes (min 44x44px)
- Readable font sizes on all devices

## Error States
- **No articles:** Show empty state with illustration
- **Loading error:** Show error message with retry button
- **Network offline:** Show offline indicator

## Maintenance
- Update this SOP when UI changes
- Document new components added
- Keep design system in sync with `gemini.md`
