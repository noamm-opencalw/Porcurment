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
    title: 'Sony WH-1000XM5 אוזניות אלחוטיות עם מסנן רעשים',
    description: 'ביטול רעשים מוביל בתעשייה עם Auto NC Optimizer. שיחות ברורות עם 4 מיקרופונים. עד 30 שעות סוללה עם טעינה מהירה.',
    price: '₪1,029.00',
    price_numeric: 1029.00,
    url: '#',
    phone: '03-9419691',
    seller: 'KSP',
    verdict: 'BUY',
    explanation: 'המחיר הטוב ביותר ממשווק מורשה עם אחריות מלאה. מדיניות החזרה של 14 יום. המחיר נמוך ב-18% מהממוצע בשוק של ₪1,249.',
    risk_level: 'low',
    risk_notes: 'אין',
    negotiation_strategy: 'בדקו קופונים פעילים באתר. לקוחות מועדון KSP מקבלים הנחה נוספת.',
    score_breakdown: { price: 9, reliability: 10, total_cost: 9, authenticity: 10, protection: 8 },
    total_score: 92,
  },
  {
    rank: 2,
    title: 'Bose QuietComfort Ultra — אוזניות מחודשות',
    description: 'אוזניות Bose QC Ultra מחודשות עם שמע מרחבי וטכנולוגיית CustomTune. כולל 90 יום אחריות. ביטול רעשים מצוין.',
    price: '₪899.00',
    price_numeric: 899.00,
    url: '#',
    phone: '03-6245555',
    seller: 'Ivory',
    verdict: 'NEGOTIATE',
    explanation: 'המחיר הנמוך ביותר — ₪400 מתחת למחיר הקמעונאי. מוצר מחודש ממשווק מורשה עם אחריות. אידיאלי למודעי תקציב.',
    risk_level: 'medium',
    risk_notes: 'מחודש — ייתכנו סימני שימוש קוסמטיים. אחריות 90 יום בלבד.',
    negotiation_strategy: 'שאלו על יחידות open-box עם אריזה מקורית. בקשו התאמת מחיר מול חנויות אחרות.',
    score_breakdown: { price: 10, reliability: 8, total_cost: 9, authenticity: 7, protection: 6 },
    total_score: 81,
  },
  {
    rank: 3,
    title: 'Apple AirPods Max — Lightning (דור קודם)',
    description: 'איכות בנייה פרימיום עם שמע חישובי, שמע מרחבי עם מעקב ראש דינמי, וביטול רעשים אקטיבי. מחיר מבצע על הדור הקודם.',
    price: '₪749.00',
    price_numeric: 749.00,
    url: '#',
    phone: '*6282',
    seller: 'Bug',
    verdict: 'BUY',
    explanation: 'ערך מדהים — 64% הנחה ממחיר ₪2,049. חדש לגמרי עם אחריות Apple מלאה. גרסת Lightning במבצע בגלל המעבר ל-USB-C — אותה איכות שמע.',
    risk_level: 'low',
    risk_notes: 'חיבור Lightning — ללא USB-C. ייתכן שלא יקבל עדכוני firmware עתידיים.',
    negotiation_strategy: 'בדקו משלוח חינם. שלבו עם כרטיס אשראי שמציע קאשבק.',
    score_breakdown: { price: 10, reliability: 9, total_cost: 9, authenticity: 9, protection: 5 },
    total_score: 78,
  },
];

export const DEMO_SUMMARY = 'לאחר ניתוח 10 עסקאות בקמעונאים מרכזיים, פלטפורמות סיטונאיות ומשווקים מורשים בישראל, זיהינו שלוש אפשרויות מצוינות. ה-Sony WH-1000XM5 מ-KSP מציע את האיזון הטוב ביותר בין מחיר, אמינות ותכונות. כל הבחירות המובילות כוללות משלוח חינם והגנת קונה חזקה.';

export const DEMO_ALL_DEALS = [
  ...DEMO_DEALS,
  { rank: 4, title: 'Sennheiser Momentum 4 Wireless', price: '₪1,199.00', price_numeric: 1199.00, seller: 'iDigital', verdict: 'NEGOTIATE', total_score: 74, risk_level: 'low' },
  { rank: 5, title: 'Sony WH-1000XM4 (דור קודם)', price: '₪749.00', price_numeric: 749.00, seller: 'Zap', verdict: 'NEGOTIATE', total_score: 69, risk_level: 'medium' },
  { rank: 6, title: 'JBL Tour One M2 Wireless NC', price: '₪799.00', price_numeric: 799.00, seller: 'Machsanei Hashmal', verdict: 'PASS', total_score: 62, risk_level: 'low' },
  { rank: 7, title: 'Beats Studio Pro', price: '₪679.00', price_numeric: 679.00, seller: 'Amazon.co.il', verdict: 'PASS', total_score: 58, risk_level: 'low' },
  { rank: 8, title: 'Bowers & Wilkins PX7 S2e', price: '₪1,399.00', price_numeric: 1399.00, seller: 'iDigital', verdict: 'PASS', total_score: 55, risk_level: 'low' },
];

export const DEMO_HISTORY = [
  { id: 1, product_query: 'אוזניות עם מסנן רעשים', status: 'completed', deals_found: 3, started_at: '2026-03-30T10:24:00Z' },
  { id: 2, product_query: 'כיסא משרדי ארגונומי', status: 'completed', deals_found: 3, started_at: '2026-03-29T15:15:00Z' },
  { id: 3, product_query: 'מסך 27 אינץ 4K', status: 'completed', deals_found: 3, started_at: '2026-03-28T11:42:00Z' },
  { id: 4, product_query: 'מכונת קפה תעשייתית', status: 'failed', deals_found: 0, started_at: '2026-03-27T09:05:00Z' },
  { id: 5, product_query: 'שולחן עמידה מתכוונן', status: 'completed', deals_found: 3, started_at: '2026-03-26T14:30:00Z' },
  { id: 6, product_query: 'מקלדת ועכבר אלחוטיים', status: 'completed', deals_found: 3, started_at: '2026-03-25T16:18:00Z' },
];
