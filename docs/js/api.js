/* Porcurment — API Client & Data Layer */

// Backend URL — change for production deployment
const API_BASE = 'http://localhost:5000';

// ---- API calls (for when Flask backend is running) ----

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

// ---- Demo data (used when no backend is available) ----

export const DEMO_DEALS = [
  {
    rank: 1,
    title: 'Sony WH-1000XM5 Wireless Noise Cancelling Headphones',
    description: 'Industry-leading noise cancellation with Auto NC Optimizer. Crystal clear hands-free calling with 4 beamforming microphones. Up to 30 hours battery life with quick charging.',
    price: '$278.00',
    price_numeric: 278.00,
    url: '#',
    phone: '1-888-280-4331',
    seller: 'Amazon',
    verdict: 'BUY',
    explanation: "Best price from an authorized reseller with full warranty. Amazon's 30-day return policy is risk-free. Price is 18% below the market average of $339.",
    risk_level: 'low',
    risk_notes: 'None',
    negotiation_strategy: 'Check for active Amazon coupons. Subscribe & Save may offer an additional 5% discount.',
    score_breakdown: { price: 9, reliability: 10, total_cost: 9, authenticity: 10, protection: 8 },
    total_score: 92,
  },
  {
    rank: 2,
    title: 'Bose QuietComfort Ultra Headphones — Renewed',
    description: 'Renewed/refurbished Bose QC Ultra with spatial audio and CustomTune technology. Includes 90-day Best Buy warranty. Excellent noise cancellation with Quiet and Aware modes.',
    price: '$249.99',
    price_numeric: 249.99,
    url: '#',
    phone: '1-888-237-8289',
    seller: 'Best Buy Outlet',
    verdict: 'NEGOTIATE',
    explanation: 'Lowest absolute price at $100 below retail. Refurbished from authorized retailer with warranty. Ideal if budget-conscious.',
    risk_level: 'medium',
    risk_notes: 'Refurbished — cosmetic wear possible. 90-day warranty only.',
    negotiation_strategy: 'Ask about open-box units with original packaging. Price-match with other outlet stores.',
    score_breakdown: { price: 10, reliability: 8, total_cost: 9, authenticity: 7, protection: 6 },
    total_score: 81,
  },
  {
    rank: 3,
    title: 'Apple AirPods Max — Lightning (Previous Gen)',
    description: 'Premium build quality with computational audio, spatial audio with dynamic head tracking, and Active Noise Cancellation. Clearance pricing on previous generation.',
    price: '$199.00',
    price_numeric: 199.00,
    url: '#',
    phone: '1-800-925-6278',
    seller: 'Walmart',
    verdict: 'BUY',
    explanation: 'Incredible value at 64% off $549 MSRP. Brand new with full Apple warranty. Lightning version cleared due to USB-C update — same audio quality.',
    risk_level: 'low',
    risk_notes: 'Lightning connector — no USB-C. May not receive future firmware updates.',
    negotiation_strategy: 'Check Walmart+ for free next-day delivery. Stack with cashback browser extensions.',
    score_breakdown: { price: 10, reliability: 9, total_cost: 9, authenticity: 9, protection: 5 },
    total_score: 78,
  },
];

export const DEMO_SUMMARY = 'After analyzing 10 deals across major retailers, wholesale platforms, and authorized resellers, we identified three outstanding options. The Sony WH-1000XM5 from Amazon offers the best balance of price, reliability, and features. All top picks include free shipping and strong buyer protection.';

export const DEMO_ALL_DEALS = [
  ...DEMO_DEALS,
  { rank: 4, title: 'Sennheiser Momentum 4 Wireless', price: '$299.95', price_numeric: 299.95, seller: 'B&H Photo', verdict: 'NEGOTIATE', total_score: 74, risk_level: 'low' },
  { rank: 5, title: 'Sony WH-1000XM4 (Previous Gen)', price: '$198.00', price_numeric: 198.00, seller: 'eBay', verdict: 'NEGOTIATE', total_score: 69, risk_level: 'medium' },
  { rank: 6, title: 'JBL Tour One M2 Wireless NC', price: '$199.95', price_numeric: 199.95, seller: 'JBL.com', verdict: 'PASS', total_score: 62, risk_level: 'low' },
  { rank: 7, title: 'Beats Studio Pro', price: '$179.99', price_numeric: 179.99, seller: 'Target', verdict: 'PASS', total_score: 58, risk_level: 'low' },
  { rank: 8, title: 'Bowers & Wilkins PX7 S2e', price: '$349.00', price_numeric: 349.00, seller: 'Crutchfield', verdict: 'PASS', total_score: 55, risk_level: 'low' },
];

export const DEMO_HISTORY = [
  { id: 1, product_query: 'Noise Cancelling Headphones', status: 'completed', deals_found: 3, started_at: '2026-03-30T10:24:00Z' },
  { id: 2, product_query: 'Ergonomic Office Chair', status: 'completed', deals_found: 3, started_at: '2026-03-29T15:15:00Z' },
  { id: 3, product_query: '27 inch 4K Monitor', status: 'completed', deals_found: 3, started_at: '2026-03-28T11:42:00Z' },
  { id: 4, product_query: 'Industrial Coffee Machine', status: 'failed', deals_found: 0, started_at: '2026-03-27T09:05:00Z' },
  { id: 5, product_query: 'Standing Desk Converter', status: 'completed', deals_found: 3, started_at: '2026-03-26T14:30:00Z' },
  { id: 6, product_query: 'Wireless Keyboard and Mouse Combo', status: 'completed', deals_found: 3, started_at: '2026-03-25T16:18:00Z' },
];
