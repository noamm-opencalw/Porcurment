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
        <h1>מצא את העסקאות הטובות ביותר</h1>
        <p>סוכני הרכש החכמים שלנו סורקים את האינטרנט, משווים מחירים וממליצים על 3 העסקאות המובילות — כדי שלא תצטרכו לעשות את זה בעצמכם.</p>
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
              placeholder="איזה מוצר אתם מחפשים?"
              autocomplete="off"
              required
            >
            <button type="submit" class="btn btn-filled btn-lg">
              ${icon('bolt', 20)} מצא עסקאות
            </button>
          </div>
        </form>

        <div class="home-suggestions" id="suggestions">
          <button class="chip" data-query="מקלדת אלחוטית">מקלדת אלחוטית</button>
          <button class="chip" data-query="כיסא משרדי ארגונומי">כיסא משרדי ארגונומי</button>
          <button class="chip" data-query="מסך 27 אינץ 4K">מסך 27 אינץ׳ 4K</button>
          <button class="chip" data-query="אוזניות עם מסנן רעשים">אוזניות עם מסנן רעשים</button>
          <button class="chip" data-query="שולחן עמידה מתכוונן">שולחן עמידה מתכוונן</button>
        </div>
      </section>

      <section class="home-features">
        <div class="chip chip--filled">${icon('travel_explore', 18)} חיפוש ממקורות מרובים</div>
        <div class="chip chip--filled">${icon('analytics', 18)} ניתוח מבוסס AI</div>
        <div class="chip chip--filled">${icon('verified', 18)} אימות מחירים</div>
        <div class="chip chip--filled">${icon('shield', 18)} הערכת סיכונים</div>
        <div class="chip chip--filled">${icon('mail', 18)} דוחות במייל</div>
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
    showLoading('מחפשים את העסקאות הטובות ביותר', `מחפשים "${q}"...`);
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
  const query = queryFromHash || 'אוזניות עם מסנן רעשים';
  const deals = DEMO_DEALS;
  const allDeals = DEMO_ALL_DEALS;
  const summary = DEMO_SUMMARY;

  return `
    <div class="view-enter">
      <div class="results-header">
        <h1>המלצות עסקאות</h1>
        <p class="query-label">תוצאות עבור <strong>${query}</strong></p>
      </div>

      <div class="summary-card">
        <div class="summary-card__label">
          ${icon('auto_awesome', 20)} סיכום מנהלים
        </div>
        <p>${summary}</p>
      </div>

      <div class="deals-grid">
        ${deals.map(d => renderDealCard(d)).join('')}
      </div>

      <div class="comparison-section">
        <h2>השוואת כל העסקאות</h2>
        ${renderComparisonTable(allDeals)}
      </div>

      <div class="results-actions">
        <a href="#/" class="btn btn-outlined">
          ${icon('search', 18)} חיפוש חדש
        </a>
        <button class="btn btn-tonal" onclick="window.__toast('ייצוא CSV זמין באפליקציית Flask המלאה')">
          ${icon('download', 18)} ייצוא CSV
        </button>
        <a href="#/history" class="btn btn-outlined">
          ${icon('history', 18)} צפה בהיסטוריה
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
          <h1>היסטוריית חיפושים</h1>
          <p>החיפושים הקודמים שלכם וההמלצות השמורות</p>
        </div>
        <div class="empty-state">
          ${icon('inbox', 64)}
          <h3>אין חיפושים עדיין</h3>
          <p>התחילו בחיפוש מוצר כדי למצוא את העסקאות הטובות ביותר.</p>
          <a href="#/" class="btn btn-filled" style="margin-top:20px">
            ${icon('search', 18)} התחילו לחפש
          </a>
        </div>
      </div>`;
  }

  return `
    <div class="view-enter">
      <div class="history-header">
        <h1>היסטוריית חיפושים</h1>
        <p>החיפושים הקודמים שלכם וההמלצות השמורות</p>
      </div>
      <div class="history-list">
        ${searches.map(s => renderHistoryCard(s)).join('')}
      </div>
    </div>`;
}

export function initHistory() {
  // History card clicks are handled via onclick in renderHistoryCard
}
