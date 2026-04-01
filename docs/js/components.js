/* פורקורמנט — Reusable UI Components */

import { icon } from './icons.js';

// ---- Toast ----
export function showToast(message, duration = 3000) {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 300ms ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ---- Loading overlay ----
const STAGES = [
  { key: 'search', label: 'מחפש בחנויות וספקים...' },
  { key: 'analyze', label: 'מנתח ומשווה מחירים...' },
  { key: 'rank', label: 'מדרג את העסקאות המובילות...' },
];

let stageIndex = 0;
let stageTimer = null;

export function showLoading(title, subtitle) {
  const overlay = document.getElementById('loading-overlay');
  if (!overlay) return;
  if (title) document.getElementById('loading-title').textContent = title;
  if (subtitle) document.getElementById('loading-subtitle').textContent = subtitle;

  const stagesEl = document.getElementById('loading-stages');
  stagesEl.innerHTML = STAGES.map((s, i) =>
    `<div class="loading-stage${i === 0 ? ' active' : ''}" id="stage-${s.key}">
      ${icon(i === 0 ? 'pending' : 'circle', 20)}
      ${s.label}
    </div>`
  ).join('');

  overlay.classList.add('active');
  stageIndex = 0;

  // Stages advance every 15s (real searches take 30-60s+)
  stageTimer = setInterval(() => {
    stageIndex++;
    if (stageIndex >= STAGES.length) { stageIndex = STAGES.length - 1; return; }
    STAGES.forEach((s, i) => {
      const el = document.getElementById(`stage-${s.key}`);
      if (!el) return;
      el.className = 'loading-stage';
      if (i < stageIndex) {
        el.classList.add('done');
        el.querySelector('.material-symbols-rounded').textContent = 'check_circle';
      } else if (i === stageIndex) {
        el.classList.add('active');
        el.querySelector('.material-symbols-rounded').textContent = 'pending';
      }
    });
  }, 15000);
}

export function hideLoading() {
  document.getElementById('loading-overlay')?.classList.remove('active');
  if (stageTimer) { clearInterval(stageTimer); stageTimer = null; }
}

// ---- Deal Card ----
export function renderDealCard(deal) {
  const rank = deal.rank || 1;
  const medals = ['🏆', '🥈', '🥉'];
  const medal = medals[rank - 1] || `#${rank}`;
  const verified = deal.price_verified ? `${icon('verified', 14)}` : '';

  return `
    <div class="deal-card">
      <div class="deal-card__top">
        <span class="deal-card__medal">${medal}</span>
        <span class="deal-card__price">${deal.price || '?'}${verified}</span>
      </div>
      <div class="deal-card__title">${(deal.title || '').substring(0, 60)}</div>
      <div class="deal-card__seller">${icon('store', 14)} ${deal.seller || ''}</div>
      ${deal.verdict ? `<div class="deal-card__verdict">${deal.verdict}</div>` : ''}
      ${deal.url ? `
        <a href="${deal.url}" target="_blank" rel="noopener" class="deal-card__link">
          ${icon('open_in_new', 16)} לעסקה
        </a>` : ''}
    </div>`;
}

// ---- History Card ----
export function renderHistoryCard(search) {
  const statusIcon = search.status === 'completed' ? 'check_circle' :
                     search.status === 'failed' ? 'error' : 'pending';
  const statusClass = search.status;
  const date = new Date(search.started_at || search.created_at);
  const dateStr = date.toLocaleDateString('he-IL', { day: 'numeric', month: 'numeric', year: 'numeric' }) +
                  ' בשעה ' + date.toLocaleTimeString('he-IL', { hour: 'numeric', minute: '2-digit' });
  const meta = search.status === 'completed' ? 'הושלם' :
               search.status === 'failed' ? 'נכשל' : 'רץ...';

  return `
    <div class="history-card" data-id="${search.id}">
      <div class="history-card__main" onclick="window.location.hash='#/results/${search.id}'">
        <div class="history-card__icon history-card__icon--${statusClass}">
          ${icon(statusIcon)}
        </div>
        <div class="history-card__content">
          <div class="history-card__query">${search.product_query}</div>
          <div class="history-card__meta">
            <span>${meta}</span>
            <span>${dateStr}</span>
          </div>
        </div>
        <span class="material-symbols-rounded history-card__arrow">chevron_left</span>
      </div>
      <button class="btn btn-tonal btn-sm history-card__research" data-query="${search.product_query}">
        ${icon('refresh', 16)} חפש מחדש
      </button>
    </div>`;
}

// ---- Comparison Table ----
export function renderComparisonTable(deals) {
  const rows = deals.map(d => {
    const price = d.price || 'לא זמין';
    const titleShort = (d.title || '').substring(0, 45) + ((d.title || '').length > 45 ? '...' : '');
    const link = d.url ? `<a href="${d.url}" target="_blank" rel="noopener">${titleShort}</a>` : titleShort;
    return `<tr>
      <td><strong>#${d.rank || ''}</strong></td>
      <td>${link}</td>
      <td class="table-price">${price}</td>
      <td>${d.seller || 'לא זמין'}</td>
      <td>${d.verdict || ''}</td>
      <td>${d.total_score || '-'}</td>
    </tr>`;
  }).join('');

  return `
    <div class="data-table-wrapper">
      <table class="data-table">
        <thead>
          <tr><th>#</th><th>מוצר</th><th>מחיר</th><th>חנות</th><th>המלצה</th><th>ציון</th></tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
}

// ---- Animate score bars on view ----
export function animateScoreBars() {
  const bars = document.querySelectorAll('.score-bar-fill');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const bar = entry.target;
        setTimeout(() => { bar.style.width = bar.dataset.width + '%'; }, 100);
        observer.unobserve(bar);
      }
    });
  }, { threshold: 0.1 });
  bars.forEach(bar => observer.observe(bar));
}
