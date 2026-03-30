/* DealFinder — View Renderers */

import { icon } from './icons.js';
import { renderDealCard, renderHistoryCard, renderComparisonTable, animateScoreBars, showLoading, hideLoading, showToast } from './components.js';
import { DEMO_DEALS, DEMO_SUMMARY, DEMO_ALL_DEALS, DEMO_HISTORY, searchState, findClarification } from './api.js';

window.__toast = showToast;

// =====================
// HOME VIEW
// =====================
export function renderHome() {
  return `
    <div class="view-enter">
      <section class="home-hero">
        <div class="home-hero__icon">
          ${icon('bolt', 40)}
        </div>
        <h1>Find the best deal</h1>
        <p>AI scans suppliers, compares prices, returns top 3.</p>
      </section>

      <section class="home-search">
        <form id="search-form">
          <div class="search-box">
            <div class="search-box__icon">
              ${icon('search')}
            </div>
            <input
              type="text"
              id="search-input"
              class="search-box__input"
              placeholder="What are you looking for?"
              autocomplete="off"
              required
            >
            <button type="submit" class="btn btn-filled btn-lg">
              ${icon('bolt', 20)} Search
            </button>
          </div>
        </form>

        <div class="home-suggestions" id="suggestions">
          <button class="chip" data-query="wireless keyboard">wireless keyboard</button>
          <button class="chip" data-query="ergonomic office chair">ergonomic chair</button>
          <button class="chip" data-query="27 inch 4K monitor">27" 4K monitor</button>
          <button class="chip" data-query="noise cancelling headphones">NC headphones</button>
          <button class="chip" data-query="standing desk">standing desk</button>
        </div>
      </section>
    </div>`;
}

function startSearch(query) {
  // Store the refined query and generate demo results for it
  // searchState.query may already be set by clarification dialog (original query)
  if (!searchState.query) searchState.query = query;
  searchState.refinedQuery = query;
  searchState.deals = DEMO_DEALS;
  searchState.allDeals = DEMO_ALL_DEALS;
  searchState.summary = `Analyzed 10 deals from major retailers for "${query}". Top picks include free shipping and buyer protection.`;

  showLoading('Finding best deals', `Searching "${query}"...`);
  setTimeout(() => {
    hideLoading();
    window.location.hash = `#/results?q=${encodeURIComponent(query)}`;
  }, 2800);
}

function showClarificationDialog(originalQuery, rule) {
  const existing = document.getElementById('clarification-overlay');
  if (existing) existing.remove();

  const overlay = document.createElement('div');
  overlay.id = 'clarification-overlay';
  overlay.className = 'clarification-overlay active';
  overlay.innerHTML = `
    <div class="clarification-card">
      <div class="clarification-card__icon">
        ${icon('help', 32)}
      </div>
      <h3 class="clarification-card__title">${rule.question}</h3>
      <p class="clarification-card__subtitle">You searched for <strong>"${originalQuery}"</strong> — help us find exactly what you need:</p>
      <div class="clarification-options" id="clarification-options">
        ${rule.options.map(opt => `
          <button class="clarification-option" data-value="${opt.value}">
            ${opt.label}
          </button>
        `).join('')}
      </div>
      <button class="btn btn-outlined clarification-skip" id="clarification-skip">
        Search as is: "${originalQuery}"
      </button>
    </div>
  `;
  document.body.appendChild(overlay);

  // Handle option selection — save original query for display
  document.getElementById('clarification-options')?.addEventListener('click', (e) => {
    const btn = e.target.closest('.clarification-option');
    if (!btn) return;
    overlay.remove();
    searchState.query = originalQuery;
    startSearch(btn.dataset.value);
  });

  // Handle skip — original = refined
  document.getElementById('clarification-skip')?.addEventListener('click', () => {
    overlay.remove();
    startSearch(originalQuery);
  });

  // Close on overlay background click
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
      overlay.remove();
    }
  });
}

export function initHome() {
  document.getElementById('search-form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const input = document.getElementById('search-input');
    const q = input?.value.trim();
    if (!q) { input?.focus(); return; }

    // Reset state for new search
    searchState.query = null;
    searchState.refinedQuery = null;

    // Check if we need clarification
    const rule = findClarification(q);
    if (rule) {
      showClarificationDialog(q, rule);
    } else {
      startSearch(q);
    }
  });

  document.getElementById('suggestions')?.addEventListener('click', (e) => {
    const chip = e.target.closest('.chip');
    if (!chip) return;
    const query = chip.dataset.query;
    const input = document.getElementById('search-input');
    if (input) { input.value = query; input.focus(); }
  });
}

// =====================
// RESULTS VIEW
// =====================
export function renderResults(queryFromHash) {
  const query = searchState.refinedQuery || queryFromHash || 'noise cancelling headphones';
  const deals = searchState.deals || DEMO_DEALS;
  const allDeals = searchState.allDeals || DEMO_ALL_DEALS;
  const summary = searchState.summary || DEMO_SUMMARY;

  // Show the original query if it was refined
  const originalQuery = searchState.query;
  const wasRefined = originalQuery && originalQuery !== query;

  return `
    <div class="view-enter">
      <div class="results-header">
        <p class="query-label">Results for <strong>${query}</strong></p>
        ${wasRefined ? `<p class="query-refined">Original search: "${originalQuery}" &rarr; refined to "${query}"</p>` : ''}
      </div>

      <div class="summary-card">
        <div class="summary-card__label">
          ${icon('auto_awesome', 20)} AI Summary
        </div>
        <p>${summary}</p>
      </div>

      <div class="deals-grid">
        ${deals.map(d => renderDealCard(d)).join('')}
      </div>

      <div class="comparison-section">
        <h2>All deals</h2>
        ${renderComparisonTable(allDeals)}
      </div>

      <div class="results-actions">
        <a href="#/" class="btn btn-outlined">
          ${icon('search', 18)} New search
        </a>
        <button class="btn btn-tonal" onclick="window.__toast('CSV export available in full app')">
          ${icon('download', 18)} Export CSV
        </button>
      </div>
    </div>`;
}

export function initResults() {
  animateScoreBars();
}

// =====================
// HISTORY VIEW
// =====================
export function renderHistory() {
  const searches = DEMO_HISTORY;

  if (!searches.length) {
    return `
      <div class="view-enter">
        <div class="history-header">
          <h1>History</h1>
        </div>
        <div class="empty-state">
          ${icon('inbox', 64)}
          <h3>No searches yet</h3>
          <p>Search for a product to get started.</p>
          <a href="#/" class="btn btn-filled" style="margin-top:20px">
            ${icon('search', 18)} Search
          </a>
        </div>
      </div>`;
  }

  return `
    <div class="view-enter">
      <div class="history-header">
        <h1>History</h1>
      </div>
      <div class="history-list">
        ${searches.map(s => renderHistoryCard(s)).join('')}
      </div>
    </div>`;
}

export function initHistory() {}
