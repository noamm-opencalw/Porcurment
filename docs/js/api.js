/* DealFinder — API Client & Data Layer */

const API_BASE = 'http://localhost:5000';

// ---- API calls ----

export async function searchDeals(productQuery) {
  const form = new FormData();
  form.append('product_query', productQuery);
  const resp = await fetch(`${API_BASE}/search`, { method: 'POST', body: form });
  return resp.json();
}

export async function getSearchHistory() {
  const resp = await fetch(`${API_BASE}/api/history`);
  return resp.json();
}

export async function getSearchResult(searchId) {
  const resp = await fetch(`${API_BASE}/api/results/${searchId}`);
  return resp.json();
}

// ---- Demo data ----

export const DEMO_DEALS = [
  {
    rank: 1,
    title: 'Sony WH-1000XM5 Wireless Noise Cancelling Headphones',
    description: 'Industry-leading NC with Auto NC Optimizer. 4 mics for clear calls. 30hr battery.',
    price: '₪1,029',
    price_numeric: 1029.00,
    url: '#',
    phone: '03-9419691',
    seller: 'KSP',
    verdict: 'BUY',
    explanation: 'Best price from authorized dealer with full warranty. 18% below market average of ₪1,249.',
    risk_level: 'low',
    risk_notes: 'None',
    negotiation_strategy: 'Check for active coupons. Club members get extra discount.',
    score_breakdown: { price: 9, reliability: 10, total_cost: 9, authenticity: 10, protection: 8 },
    total_score: 92,
  },
  {
    rank: 2,
    title: 'Bose QuietComfort Ultra — Refurbished',
    description: 'Spatial audio with CustomTune. 90-day warranty. Excellent noise cancellation.',
    price: '₪899',
    price_numeric: 899.00,
    url: '#',
    phone: '03-6245555',
    seller: 'Ivory',
    verdict: 'NEGOTIATE',
    explanation: 'Lowest price — ₪400 below retail. Refurbished from authorized dealer.',
    risk_level: 'medium',
    risk_notes: 'Refurbished — cosmetic wear possible. 90-day warranty only.',
    negotiation_strategy: 'Ask about open-box units with original packaging.',
    score_breakdown: { price: 10, reliability: 8, total_cost: 9, authenticity: 7, protection: 6 },
    total_score: 81,
  },
  {
    rank: 3,
    title: 'Apple AirPods Max — Lightning (Previous Gen)',
    description: 'Premium build, spatial audio with head tracking, active noise cancellation.',
    price: '₪749',
    price_numeric: 749.00,
    url: '#',
    phone: '*6282',
    seller: 'Bug',
    verdict: 'BUY',
    explanation: '64% off retail ₪2,049. Brand new with full Apple warranty. Lightning clearance.',
    risk_level: 'low',
    risk_notes: 'Lightning connector — no USB-C.',
    negotiation_strategy: 'Check for free shipping. Combine with cashback credit card.',
    score_breakdown: { price: 10, reliability: 9, total_cost: 9, authenticity: 9, protection: 5 },
    total_score: 78,
  },
];

export const DEMO_SUMMARY = 'Analyzed 10 deals from major retailers. Sony WH-1000XM5 from KSP offers the best balance of price, reliability and features. All top picks include free shipping and buyer protection.';

export const DEMO_ALL_DEALS = [
  ...DEMO_DEALS,
  { rank: 4, title: 'Sennheiser Momentum 4 Wireless', price: '₪1,199', price_numeric: 1199.00, seller: 'iDigital', verdict: 'NEGOTIATE', total_score: 74, risk_level: 'low' },
  { rank: 5, title: 'Sony WH-1000XM4 (Previous Gen)', price: '₪749', price_numeric: 749.00, seller: 'Zap', verdict: 'NEGOTIATE', total_score: 69, risk_level: 'medium' },
  { rank: 6, title: 'JBL Tour One M2 Wireless NC', price: '₪799', price_numeric: 799.00, seller: 'Machsanei Hashmal', verdict: 'PASS', total_score: 62, risk_level: 'low' },
  { rank: 7, title: 'Beats Studio Pro', price: '₪679', price_numeric: 679.00, seller: 'Amazon.co.il', verdict: 'PASS', total_score: 58, risk_level: 'low' },
  { rank: 8, title: 'Bowers & Wilkins PX7 S2e', price: '₪1,399', price_numeric: 1399.00, seller: 'iDigital', verdict: 'PASS', total_score: 55, risk_level: 'low' },
];

export const DEMO_HISTORY = [
  { id: 1, product_query: 'Noise cancelling headphones', status: 'completed', deals_found: 3, started_at: '2026-03-30T10:24:00Z' },
  { id: 2, product_query: 'Ergonomic office chair', status: 'completed', deals_found: 3, started_at: '2026-03-29T15:15:00Z' },
  { id: 3, product_query: '27" 4K monitor', status: 'completed', deals_found: 3, started_at: '2026-03-28T11:42:00Z' },
  { id: 4, product_query: 'Industrial coffee machine', status: 'failed', deals_found: 0, started_at: '2026-03-27T09:05:00Z' },
  { id: 5, product_query: 'Standing desk', status: 'completed', deals_found: 3, started_at: '2026-03-26T14:30:00Z' },
  { id: 6, product_query: 'Wireless keyboard & mouse', status: 'completed', deals_found: 3, started_at: '2026-03-25T16:18:00Z' },
];
