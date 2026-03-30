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
  const verdict = (deal.verdict || 'PASS').toUpperCase();
  const risk = (deal.risk_level || 'medium').toLowerCase();

  const verdictLabels = { BUY: 'קנה', NEGOTIATE: 'נהל מו״מ', PASS: 'דלג' };
  const verdictIcons = { BUY: 'thumb_up', NEGOTIATE: 'handshake', PASS: 'block' };
  const riskLabels = { low: 'סיכון נמוך', medium: 'סיכון בינוני', high: 'סיכון גבוה' };

  return `
    <div class="deal-card">
      <div class="deal-card__header">
        <div class="deal-card__rank deal-card__rank--${rank}">#${rank}</div>
        <div class="deal-card__price">${deal.price || 'לא זמין'}</div>
      </div>
      <div class="deal-card__body">
        <h3 class="deal-card__title">${deal.title || 'מוצר לא ידוע'}</h3>
        <div class="deal-card__seller">
          ${icon('store', 16)} <strong>${deal.seller || 'לא ידוע'}</strong>
        </div>
        <div class="deal-card__badges">
          <span class="badge badge-${verdict.toLowerCase()}">
            ${icon(verdictIcons[verdict] || 'block', 14)}
            ${verdictLabels[verdict] || 'דלג'}
          </span>
          <span class="badge badge-risk-${risk}">${riskLabels[risk] || 'סיכון בינוני'}</span>
        </div>

        ${deal.explanation ? `<p class="deal-card__why">${deal.explanation}</p>` : ''}

        <div class="deal-card__contacts">
          ${deal.phone && deal.phone !== 'N/A' ? `
            <a href="tel:${deal.phone}" class="deal-card__contact deal-card__contact--phone">
              ${icon('call', 18)}
              <span>${deal.phone}</span>
            </a>` : ''}
        </div>
      </div>
      <div class="deal-card__actions">
        ${deal.url && deal.url !== '#' ? `
          <a href="${deal.url}" target="_blank" rel="noopener" class="btn btn-filled btn-block">
            ${icon('open_in_new', 18)} צפה בעסקה
          </a>` : `
          <span class="btn btn-filled btn-block btn-disabled">
            ${icon('link_off', 18)} אין קישור
          </span>`}
      </div>
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
  const verdictLabels = { BUY: 'קנה', NEGOTIATE: 'מו״מ', PASS: 'דלג' };

  const rows = deals.map(d => {
    const v = (d.verdict || 'PASS').toUpperCase();
    const price = d.price_numeric ? `₪${d.price_numeric.toFixed(0)}` : (d.price || 'לא זמין');
    return `<tr>
      <td><strong>#${d.rank || ''}</strong></td>
      <td>${(d.title || '').substring(0, 40)}${(d.title || '').length > 40 ? '...' : ''}</td>
      <td class="table-price">${price}</td>
      <td>${d.seller || 'לא זמין'}</td>
      <td><span class="badge badge-${v.toLowerCase()}">${verdictLabels[v] || 'דלג'}</span></td>
      <td>${d.total_score || '-'}</td>
    </tr>`;
  }).join('');

  return `
    <div class="data-table-wrapper">
      <table class="data-table">
        <thead>
          <tr><th>#</th><th>מוצר</th><th>מחיר</th><th>מוכר</th><th>המלצה</th><th>ציון</th></tr>
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
