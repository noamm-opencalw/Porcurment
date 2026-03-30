/* Porcurment — Reusable UI Components */

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
  { key: 'search', label: 'Searching retailers & suppliers...' },
  { key: 'analyze', label: 'Analyzing & comparing prices...' },
  { key: 'rank', label: 'Ranking top deals...' },
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
  }, 6000);
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
  const breakdown = deal.score_breakdown || {};

  const scoreLabels = { price: 'Price', reliability: 'Reliability', total_cost: 'Cost', authenticity: 'Authentic', protection: 'Protection' };

  let scoreBarsHTML = '';
  for (const [key, label] of Object.entries(scoreLabels)) {
    const val = breakdown[key] || 5;
    scoreBarsHTML += `
      <div class="score-bar-row">
        <span class="score-bar-label">${label}</span>
        <div class="score-bar-track"><div class="score-bar-fill score-bar-fill--${key}" data-width="${val * 10}"></div></div>
        <span class="score-bar-value">${val}</span>
      </div>`;
  }

  return `
    <div class="deal-card">
      <div class="deal-card__header">
        <div class="deal-card__rank deal-card__rank--${rank}">#${rank}</div>
        <div class="deal-card__price">${deal.price || 'N/A'}</div>
      </div>
      <div class="deal-card__body">
        <h3 class="deal-card__title">${deal.title || 'Unknown Product'}</h3>
        <div class="deal-card__seller">
          ${icon('store', 14)} ${deal.seller || 'Unknown'}
        </div>
        <div class="deal-card__badges">
          <span class="badge badge-${verdict.toLowerCase()}">
            ${icon(verdict === 'BUY' ? 'thumb_up' : verdict === 'NEGOTIATE' ? 'handshake' : 'block', 14)}
            ${verdict}
          </span>
          <span class="badge badge-risk-${risk}">Risk: ${risk}</span>
        </div>
        <p class="deal-card__description">${deal.description || ''}</p>
        ${deal.explanation ? `
          <div class="deal-card__explanation">
            <div class="deal-card__explanation-label">Why this deal?</div>
            <p>${deal.explanation}</p>
          </div>` : ''}
        ${deal.total_score ? `
          <div class="deal-card__score">
            <div class="deal-card__score-total">
              <span class="deal-card__score-number">${Math.round(deal.total_score)}</span>
              <span class="deal-card__score-max">/ 100</span>
            </div>
            <div class="score-bars">${scoreBarsHTML}</div>
          </div>` : ''}
        <div class="deal-card__contacts">
          ${deal.phone && deal.phone !== 'N/A' ? `
            <div class="deal-card__contact">
              ${icon('call', 16)}
              <a href="tel:${deal.phone}">${deal.phone}</a>
            </div>` : ''}
        </div>
      </div>
      ${deal.negotiation_strategy ? `
        <div class="deal-card__tip">
          ${icon('lightbulb', 16)}
          <span>${deal.negotiation_strategy}</span>
        </div>` : ''}
      <div class="deal-card__actions">
        ${deal.url && deal.url !== '#' ? `
          <a href="${deal.url}" target="_blank" rel="noopener" class="btn btn-filled">
            ${icon('open_in_new', 18)} View Deal
          </a>` : `
          <button class="btn btn-filled" onclick="window.__toast('Demo — this would open the deal page')">
            ${icon('open_in_new', 18)} View Deal
          </button>`}
      </div>
    </div>`;
}

// ---- History Card ----
export function renderHistoryCard(search) {
  const statusIcon = search.status === 'completed' ? 'check_circle' :
                     search.status === 'failed' ? 'error' : 'pending';
  const statusClass = search.status;
  const date = new Date(search.started_at);
  const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) +
                  ' at ' + date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  const meta = search.status === 'completed' ? `${search.deals_found} deal${search.deals_found !== 1 ? 's' : ''} found` :
               search.status === 'failed' ? 'Search failed' : 'In progress...';

  return `
    <div class="history-card" data-id="${search.id}" onclick="window.location.hash='#/results/${search.id}'">
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
      <span class="material-symbols-rounded history-card__arrow">chevron_right</span>
    </div>`;
}

// ---- Comparison Table ----
export function renderComparisonTable(deals) {
  const rows = deals.map(d => {
    const v = (d.verdict || 'PASS').toUpperCase();
    const r = (d.risk_level || 'medium').toLowerCase();
    const price = d.price_numeric ? `$${d.price_numeric.toFixed(2)}` : (d.price || 'N/A');
    return `<tr>
      <td><strong>#${d.rank || ''}</strong></td>
      <td>${(d.title || '').substring(0, 50)}${(d.title || '').length > 50 ? '...' : ''}</td>
      <td style="font-weight:600;color:var(--md-success)">${price}</td>
      <td>${d.seller || 'N/A'}</td>
      <td><span class="badge badge-${v.toLowerCase()}">${v}</span></td>
      <td>${d.total_score || '-'}</td>
      <td><span class="badge badge-risk-${r}">${r}</span></td>
    </tr>`;
  }).join('');

  return `
    <div class="data-table-wrapper">
      <table class="data-table">
        <thead>
          <tr><th>Rank</th><th>Product</th><th>Price</th><th>Seller</th><th>Verdict</th><th>Score</th><th>Risk</th></tr>
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
