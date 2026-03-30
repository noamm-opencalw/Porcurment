/* Porcurment — View Renderers */

import { icon } from './icons.js';
import { renderDealCard, renderHistoryCard, renderComparisonTable, animateScoreBars, showLoading, hideLoading, showToast } from './components.js';
import { DEMO_DEALS, DEMO_SUMMARY, DEMO_ALL_DEALS, DEMO_HISTORY } from './api.js';

// Expose toast globally for inline onclick handlers
window.__toast = showToast;

// =====================
// HOME VIEW
// =====================
export function renderHome() {
  return `
    <div class="view-enter">
      <section class="home-hero">
        <div class="home-hero__icon">
          ${icon('storefront', 40)}
        </div>
        <h1>Find the Best Deals</h1>
        <p>Our AI procurement agents search the web, compare prices, and recommend the top 3 deals — so you don't have to.</p>
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
              placeholder="What product are you looking for?"
              autocomplete="off"
              required
            >
            <button type="submit" class="btn btn-filled btn-lg">
              ${icon('bolt', 20)} Find Deals
            </button>
          </div>
        </form>

        <div class="home-suggestions" id="suggestions">
          <button class="chip" data-query="wireless keyboard">wireless keyboard</button>
          <button class="chip" data-query="ergonomic office chair">ergonomic office chair</button>
          <button class="chip" data-query="27 inch 4K monitor">27 inch 4K monitor</button>
          <button class="chip" data-query="noise cancelling headphones">noise cancelling headphones</button>
          <button class="chip" data-query="standing desk converter">standing desk converter</button>
        </div>
      </section>

      <section class="home-features">
        <div class="chip chip--filled">${icon('travel_explore', 18)} Searches multiple sources</div>
        <div class="chip chip--filled">${icon('analytics', 18)} AI-powered analysis</div>
        <div class="chip chip--filled">${icon('verified', 18)} Price verification</div>
        <div class="chip chip--filled">${icon('shield', 18)} Risk assessment</div>
        <div class="chip chip--filled">${icon('mail', 18)} Email reports</div>
      </section>
    </div>`;
}

export function initHome() {
  // Search form
  document.getElementById('search-form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const input = document.getElementById('search-input');
    const q = input?.value.trim();
    if (!q) { input?.focus(); return; }
    showLoading('Finding the best deals', `Searching for "${q}"...`);
    // Simulate search then navigate to results
    setTimeout(() => {
      hideLoading();
      window.location.hash = `#/results?q=${encodeURIComponent(q)}`;
    }, 2800);
  });

  // Suggestion chips
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
  const query = queryFromHash || 'Noise Cancelling Headphones';
  const deals = DEMO_DEALS;
  const allDeals = DEMO_ALL_DEALS;
  const summary = DEMO_SUMMARY;

  return `
    <div class="view-enter">
      <div class="results-header">
        <h1>Deal Recommendations</h1>
        <p class="query-label">Results for <strong>${query}</strong></p>
      </div>

      <div class="summary-card">
        <div class="summary-card__label">
          ${icon('auto_awesome', 20)} Executive Summary
        </div>
        <p>${summary}</p>
      </div>

      <div class="deals-grid">
        ${deals.map(d => renderDealCard(d)).join('')}
      </div>

      <div class="comparison-section">
        <h2>All Deals Comparison</h2>
        ${renderComparisonTable(allDeals)}
      </div>

      <div class="results-actions">
        <a href="#/" class="btn btn-outlined">
          ${icon('search', 18)} New Search
        </a>
        <button class="btn btn-tonal" onclick="window.__toast('CSV export available in the full Flask app')">
          ${icon('download', 18)} Export CSV
        </button>
        <a href="#/history" class="btn btn-outlined">
          ${icon('history', 18)} View History
        </a>
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
          <h1>Search History</h1>
          <p>Your past procurement searches and saved recommendations</p>
        </div>
        <div class="empty-state">
          ${icon('inbox', 64)}
          <h3>No searches yet</h3>
          <p>Start by searching for a product to find the best deals.</p>
          <a href="#/" class="btn btn-filled" style="margin-top:20px">
            ${icon('search', 18)} Start Searching
          </a>
        </div>
      </div>`;
  }

  return `
    <div class="view-enter">
      <div class="history-header">
        <h1>Search History</h1>
        <p>Your past procurement searches and saved recommendations</p>
      </div>
      <div class="history-list">
        ${searches.map(s => renderHistoryCard(s)).join('')}
      </div>
    </div>`;
}

export function initHistory() {
  // History card clicks are handled via onclick in renderHistoryCard
}
