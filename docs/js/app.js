/* DealFinder — SPA Router & App Shell */

import { icon } from './icons.js';
import {
  renderHome, initHome,
  renderResults, initResults,
  renderHistory, initHistory,
} from './views.js';

// =============================
// ROUTER
// =============================
const routes = [
  { pattern: /^#?\/?$/, view: 'home' },
  { pattern: /^#\/results(?:\?(.*))?$/, view: 'results' },
  { pattern: /^#\/results\/(\d+)$/, view: 'results' },
  { pattern: /^#\/history$/, view: 'history' },
];

function matchRoute(hash) {
  const h = hash || '#/';
  for (const route of routes) {
    const match = h.match(route.pattern);
    if (match) return { view: route.view, params: match.slice(1) };
  }
  return { view: 'home', params: [] };
}

function getQueryParam(paramString, key) {
  if (!paramString) return null;
  const params = new URLSearchParams(paramString);
  return params.get(key);
}

async function navigate() {
  const { view, params } = matchRoute(window.location.hash);
  const app = document.getElementById('app');

  switch (view) {
    case 'home':
      app.innerHTML = renderHome();
      initHome();
      break;
    case 'results': {
      const query = getQueryParam(params[0], 'q') || 'אוזניות עם מסנן רעשים';
      app.innerHTML = renderResults(query);
      initResults();
      break;
    }
    case 'history':
      app.innerHTML = renderHistory();
      initHistory();
      break;
    default:
      app.innerHTML = renderHome();
      initHome();
  }

  updateNav(view);
  window.scrollTo({ top: 0, behavior: 'instant' });
}

// =============================
// NAV HIGHLIGHTING
// =============================
function updateNav(activeView) {
  document.querySelectorAll('.bottom-nav__item').forEach(item => {
    item.classList.toggle('active', item.dataset.view === activeView);
  });
  document.querySelectorAll('.header__nav-item').forEach(item => {
    item.classList.toggle('active', item.dataset.view === activeView);
  });
}

// =============================
// APP SHELL
// =============================
function createAppShell() {
  // Header
  const header = document.querySelector('.header__inner');
  if (header) {
    header.innerHTML = `
      <a class="header__brand" onclick="window.location.hash='#/'">
        ${icon('bolt', 28)}
        <span class="header__brand-text">DealFinder</span>
      </a>
      <nav class="header__nav">
        <a class="header__nav-item" data-view="home" onclick="window.location.hash='#/'">
          ${icon('search', 20)} Search
        </a>
        <a class="header__nav-item" data-view="results" onclick="window.location.hash='#/results'">
          ${icon('analytics', 20)} Results
        </a>
        <a class="header__nav-item" data-view="history" onclick="window.location.hash='#/history'">
          ${icon('history', 20)} History
        </a>
      </nav>
    `;
  }

  // Bottom nav (mobile)
  const bottomNav = document.getElementById('bottom-nav');
  if (bottomNav) {
    bottomNav.innerHTML = `
      <a class="bottom-nav__item" data-view="home" onclick="window.location.hash='#/'">
        ${icon('search')}
        <span>Search</span>
      </a>
      <a class="bottom-nav__item" data-view="results" onclick="window.location.hash='#/results'">
        ${icon('analytics')}
        <span>Results</span>
      </a>
      <a class="bottom-nav__item" data-view="history" onclick="window.location.hash='#/history'">
        ${icon('history')}
        <span>History</span>
      </a>
    `;
  }
}

// =============================
// INIT
// =============================
function init() {
  createAppShell();
  navigate();
  window.addEventListener('hashchange', navigate);
}

document.addEventListener('DOMContentLoaded', init);
