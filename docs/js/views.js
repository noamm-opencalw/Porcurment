/* DealFinder — View Renderers */

import { icon } from './icons.js';
import { renderDealCard, renderHistoryCard, renderComparisonTable, animateScoreBars, showLoading, hideLoading, showToast } from './components.js';
import { DEMO_DEALS, DEMO_SUMMARY, DEMO_ALL_DEALS, DEMO_HISTORY } from './api.js';

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

export function initHome() {
  document.getElementById('search-form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const input = document.getElementById('search-input');
    const q = input?.value.trim();
    if (!q) { input?.focus(); return; }
    showLoading('Finding best deals', `Searching "${q}"...`);
    setTimeout(() => {
      hideLoading();
      window.location.hash = `#/results?q=${encodeURIComponent(q)}`;
    }, 2800);
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
  const query = queryFromHash || 'noise cancelling headphones';
  const deals = DEMO_DEALS;
  const allDeals = DEMO_ALL_DEALS;
  const summary = DEMO_SUMMARY;

  return `
    <div class="view-enter">
      <div class="results-header">
        <p class="query-label">Results for <strong>${query}</strong></p>
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
