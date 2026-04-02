/* DealFinder — API Client & Data Layer (Supabase Edge Functions) */

const SUPABASE_URL = 'https://jjqpnbaoaborumkdxwri.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpqcXBuYmFvYWJvcnVta2R4d3JpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ4NzU5NTAsImV4cCI6MjA5MDQ1MTk1MH0.wC2x31hQzBMOIOVcYsFCJ_JqPeobvYJXR_bbbQJtizg';

function edgeFn(name) {
  return `${SUPABASE_URL}/functions/v1/${name}`;
}

// ---- API calls ----

export async function clarifyQuery(productQuery) {
  const resp = await fetch(edgeFn('clarify'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_query: productQuery }),
  });
  if (!resp.ok) throw new Error(`בקשת הבהרה נכשלה (${resp.status})`);
  return resp.json();
}

export async function searchDeals(productQuery, includeInternational = false) {
  const resp = await fetch(edgeFn('search'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_query: productQuery, include_international: includeInternational }),
  });
  if (!resp.ok) throw new Error(`חיפוש נכשל (${resp.status})`);
  return resp.json();
}

export async function getSearchHistory() {
  const resp = await fetch(
    `${SUPABASE_URL}/rest/v1/searches?select=id,product_query,status,created_at&order=created_at.desc&limit=50`,
    { headers: { apikey: SUPABASE_ANON_KEY, Authorization: `Bearer ${SUPABASE_ANON_KEY}` } }
  );
  if (!resp.ok) throw new Error(`טעינת היסטוריה נכשלה (${resp.status})`);
  return resp.json();
}

export async function getSearchResult(searchId) {
  const resp = await fetch(
    `${SUPABASE_URL}/rest/v1/searches?id=eq.${searchId}&select=*`,
    { headers: { apikey: SUPABASE_ANON_KEY, Authorization: `Bearer ${SUPABASE_ANON_KEY}` } }
  );
  if (!resp.ok) throw new Error(`טעינת תוצאות נכשלה (${resp.status})`);
  const rows = await resp.json();
  if (!rows.length) throw new Error('חיפוש לא נמצא');
  const row = rows[0];
  return {
    search_id: row.id,
    product_query: row.product_query,
    recommendation_summary: row.recommendation_summary || '',
    deals: row.results || [],
  };
}

export async function reportDeal(searchId, dealRank, type = 'wrong_price') {
  await fetch(
    `${SUPABASE_URL}/rest/v1/feedback`,
    {
      method: 'POST',
      headers: {
        apikey: SUPABASE_ANON_KEY,
        Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
        'Content-Type': 'application/json',
        Prefer: 'return=minimal',
      },
      body: JSON.stringify({ search_id: searchId, deal_rank: dealRank, type }),
    }
  );
}

// ---- Shared state for passing results between views ----
export const searchState = {
  query: null,
  refinedQuery: null,
  deals: null,
  allDeals: null,
  summary: null,
  reason: null,
  refinements: null,
  searchId: null,
};
