/* פורקורמנט — View Renderers */

import { icon } from './icons.js';
import { renderDealCard, renderHistoryCard, renderComparisonTable, animateScoreBars, showLoading, hideLoading, showToast } from './components.js';
import { searchDeals, clarifyQuery, getSearchHistory, getSearchResult, searchState } from './api.js';

window.__toast = showToast;

// =====================
// HOME VIEW
// =====================
export function renderHome() {
  return `
    <div class="view-enter">
      <section class="home-hero">
        <div class="home-hero__icon">
          ${icon('search_check', 36)}
        </div>
        <h1>מצא את העסקה הטובה ביותר</h1>
        <p>חיפוש חכם בין ספקים, השוואת מחירים ודירוג אוטומטי של 3 העסקאות המובילות.</p>
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
              placeholder="מה אתה מחפש?"
              autocomplete="off"
              required
            >
            <button type="submit" class="btn btn-filled btn-lg">
              ${icon('search', 20)} חיפוש
            </button>
          </div>
        </form>

        <label class="international-toggle">
          <input type="checkbox" id="include-international">
          <span>כלול גם תוצאות מאתרים בינלאומיים (Amazon, AliExpress, eBay)</span>
        </label>

        <div class="home-suggestions" id="suggestions">
          <button class="chip" data-query="מקלדת אלחוטית">מקלדת אלחוטית</button>
          <button class="chip" data-query="כיסא משרדי ארגונומי">כיסא ארגונומי</button>
          <button class="chip" data-query="מסך 27 אינץ 4K">מסך 27״ 4K</button>
          <button class="chip" data-query="אוזניות עם מסנן רעשים">אוזניות NC</button>
          <button class="chip" data-query="שולחן עמידה מתכוונן">שולחן עמידה</button>
        </div>
      </section>
    </div>`;
}

async function startSearch(query) {
  if (!searchState.query) searchState.query = query;
  searchState.refinedQuery = query;

  const includeInternational = document.getElementById('include-international')?.checked || false;

  showLoading('מחפש את העסקאות הטובות ביותר', `מחפש "${query}"...`);

  try {
    const data = await searchDeals(query, includeInternational);

    if (data.error && (!data.deals || data.deals.length === 0)) {
      hideLoading();
      showToast('שגיאה: ' + data.error);
      return;
    }

    searchState.deals = (data.deals || []).slice(0, 3);
    searchState.allDeals = data.deals || [];
    searchState.summary = data.recommendation_summary || '';
    searchState.reason = data.recommendation_reason || '';
    searchState.refinements = data.refinement_suggestions || [];
    searchState.searchId = data.search_id;

    hideLoading();
    window.location.hash = `#/results?q=${encodeURIComponent(query)}`;
  } catch (err) {
    hideLoading();
    showToast('שגיאה בחיפוש. נסה שוב.');
    console.error('Search error:', err);
  }
}

function showClarificationDialog(originalQuery, question, options) {
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
      <h3 class="clarification-card__title">${question}</h3>
      <p class="clarification-card__subtitle">חיפשת <strong>"${originalQuery}"</strong> — עזור לנו למצוא בדיוק מה שאתה צריך:</p>
      <div class="clarification-options" id="clarification-options">
        ${options.map(opt => `
          <button class="clarification-option" data-value="${originalQuery} ${opt}">
            ${opt}
          </button>
        `).join('')}
      </div>
      <button class="btn btn-outlined clarification-skip" id="clarification-skip">
        חפש כמו שזה: "${originalQuery}"
      </button>
    </div>
  `;
  document.body.appendChild(overlay);

  document.getElementById('clarification-options')?.addEventListener('click', (e) => {
    const btn = e.target.closest('.clarification-option');
    if (!btn) return;
    overlay.remove();
    searchState.query = originalQuery;
    startSearch(btn.dataset.value);
  });

  document.getElementById('clarification-skip')?.addEventListener('click', () => {
    overlay.remove();
    startSearch(originalQuery);
  });

  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
      overlay.remove();
    }
  });
}

export function initHome() {
  document.getElementById('search-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('search-input');
    const q = input?.value.trim();
    if (!q) { input?.focus(); return; }

    searchState.query = null;
    searchState.refinedQuery = null;

    try {
      showLoading('בודק את השאילתה...', `מנתח "${q}"...`);
      const clarification = await clarifyQuery(q);
      hideLoading();

      if (clarification.ready) {
        startSearch(clarification.final_query || q);
      } else {
        showClarificationDialog(q, clarification.question, clarification.options || []);
      }
    } catch (err) {
      hideLoading();
      console.error('Clarify error:', err);
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
export function renderResults(queryFromHash, searchId) {
  const query = searchState.refinedQuery || queryFromHash;
  const deals = searchState.deals;
  const allDeals = searchState.allDeals;
  const summary = searchState.summary;

  const originalQuery = searchState.query;
  const wasRefined = originalQuery && query && originalQuery !== query;

  // No results — show empty or loading state
  if (!deals || deals.length === 0) {
    if (searchId) {
      return `
        <div class="view-enter">
          <div class="results-loading">
            <div class="loading-spinner"></div>
            <p>טוען תוצאות...</p>
          </div>
        </div>`;
    }

    return `
      <div class="view-enter">
        <div class="empty-state">
          ${icon('search_off', 64)}
          <h3>אין תוצאות</h3>
          <p>חפש מוצר כדי לראות את העסקאות הטובות ביותר.</p>
          <a href="#/" class="btn btn-filled" style="margin-top:20px">
            ${icon('search', 18)} חיפוש חדש
          </a>
        </div>
      </div>`;
  }

  const top3 = deals.slice(0, 3);
  const rest = allDeals ? allDeals.slice(3) : [];
  const reason = searchState.reason || '';
  const refinements = searchState.refinements || [];

  return `
    <div class="view-enter">
      <div class="results-header">
        <p class="query-label">תוצאות עבור <strong>${query}</strong></p>
        ${wasRefined ? `<p class="query-refined">חיפוש מקורי: "${originalQuery}" &larr; מדויק ל-"${query}"</p>` : ''}
      </div>

      ${summary ? `
        <div class="summary-card">
          <div class="summary-card__label">
            ${icon('auto_awesome', 20)} סיכום AI
          </div>
          <p>${summary}</p>
          ${reason ? `<p class="summary-card__reason">${icon('info', 16)} <strong>למה נבחרה:</strong> ${reason}</p>` : ''}
        </div>` : ''}

      ${refinements.length > 0 ? `
        <div class="refinement-card">
          <div class="refinement-card__label">
            ${icon('tune', 18)} חדד את החיפוש לתוצאות מדויקות יותר:
          </div>
          <div class="refinement-chips" id="refinement-chips">
            ${refinements.map(r => `<button class="chip chip--refinement" data-query="${query} ${r}">${r}</button>`).join('')}
          </div>
        </div>` : ''}

      <div class="deals-grid">
        ${top3.map(d => renderDealCard(d)).join('')}
      </div>

      ${rest.length > 0 ? `
        <div class="comparison-section">
          <h2>${icon('list', 22)} הצעות נוספות</h2>
          ${renderComparisonTable(rest)}
        </div>` : ''}

      <div class="results-actions">
        <a href="#/" class="btn btn-outlined">
          ${icon('search', 18)} חיפוש חדש
        </a>
        <button class="btn btn-tonal" id="re-search-btn" data-query="${query}">
          ${icon('refresh', 18)} חפש מחדש
        </button>
      </div>
    </div>`;
}

export async function initResults(searchId) {
  // If navigating to a saved search, load from API
  if (searchId && searchState.searchId !== searchId) {
    try {
      const data = await getSearchResult(searchId);
      searchState.deals = (data.deals || []).slice(0, 3);
      searchState.allDeals = data.deals || [];
      searchState.summary = data.recommendation_summary || '';
      searchState.searchId = searchId;
      searchState.query = data.product_query;
      searchState.refinedQuery = data.product_query;

      const app = document.getElementById('app');
      app.innerHTML = renderResults(data.product_query, null);
    } catch (err) {
      showToast('שגיאה בטעינת תוצאות.');
      console.error('Load results error:', err);
    }
  }

  // Re-search button
  document.getElementById('re-search-btn')?.addEventListener('click', (e) => {
    const query = e.currentTarget.dataset.query;
    if (query) {
      searchState.query = null; searchState.refinedQuery = null;
      searchState.deals = null; searchState.allDeals = null;
      searchState.summary = null; searchState.reason = null;
      searchState.refinements = null; searchState.searchId = null;
      startSearch(query);
    }
  });

  // Refinement chip clicks
  document.getElementById('refinement-chips')?.addEventListener('click', (e) => {
    const chip = e.target.closest('.chip--refinement');
    if (!chip) return;
    const newQuery = chip.dataset.query;
    searchState.query = null; searchState.refinedQuery = null;
    searchState.deals = null; searchState.allDeals = null;
    searchState.summary = null; searchState.reason = null;
    searchState.refinements = null; searchState.searchId = null;
    startSearch(newQuery);
  });

  animateScoreBars();
}

// =====================
// HISTORY VIEW
// =====================
export function renderHistory() {
  return `
    <div class="view-enter">
      <div class="history-header">
        <h1>היסטוריה</h1>
      </div>
      <div id="history-content">
        <div class="results-loading">
          <div class="loading-spinner"></div>
          <p>טוען היסטוריה...</p>
        </div>
      </div>
    </div>`;
}

export async function initHistory() {
  const container = document.getElementById('history-content');
  if (!container) return;

  try {
    const searches = await getSearchHistory();

    if (!searches || searches.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          ${icon('inbox', 64)}
          <h3>אין חיפושים עדיין</h3>
          <p>חפש מוצר כדי להתחיל.</p>
          <a href="#/" class="btn btn-filled" style="margin-top:20px">
            ${icon('search', 18)} חיפוש
          </a>
        </div>`;
      return;
    }

    container.innerHTML = `
      <div class="history-list">
        ${searches.map(s => renderHistoryCard(s)).join('')}
      </div>`;

    // Wire up re-search buttons
    container.querySelectorAll('.history-card__research').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const query = e.currentTarget.dataset.query;
        if (query) {
          searchState.query = null;
          searchState.refinedQuery = null;
          searchState.deals = null;
          searchState.allDeals = null;
          searchState.summary = null;
          searchState.searchId = null;
          window.location.hash = '#/';
          setTimeout(() => {
            const input = document.getElementById('search-input');
            if (input) { input.value = query; }
            startSearch(query);
          }, 100);
        }
      });
    });
  } catch (err) {
    container.innerHTML = `
      <div class="empty-state">
        ${icon('cloud_off', 64)}
        <h3>לא ניתן לטעון היסטוריה</h3>
        <p>ודא שהשרת רץ ונסה שוב.</p>
      </div>`;
    console.error('History load error:', err);
  }
}
