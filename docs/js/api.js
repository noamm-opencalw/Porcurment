/* פורקורמנט — API Client & Data Layer */

const API_BASE = '';

// ---- API calls ----

export async function searchDeals(productQuery, includeInternational = false) {
  const resp = await fetch(`${API_BASE}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      product_query: productQuery,
      include_international: includeInternational,
    }),
  });
  if (!resp.ok) throw new Error(`חיפוש נכשל (${resp.status})`);
  return resp.json();
}

export async function getSearchHistory() {
  const resp = await fetch(`${API_BASE}/api/history`);
  if (!resp.ok) throw new Error(`טעינת היסטוריה נכשלה (${resp.status})`);
  return resp.json();
}

export async function getSearchResult(searchId) {
  const resp = await fetch(`${API_BASE}/api/results/${searchId}`);
  if (!resp.ok) throw new Error(`טעינת תוצאות נכשלה (${resp.status})`);
  return resp.json();
}

// ---- Shared state for passing results between views ----
export const searchState = {
  query: null,
  refinedQuery: null,
  deals: null,
  allDeals: null,
  summary: null,
  searchId: null,
};

// ---- Clarification questions by product category ----
export const CLARIFICATION_RULES = [
  {
    keywords: ['כיסא', 'chair'],
    question: 'למה הכיסא מיועד?',
    options: [
      { label: 'משרד / מחשב', value: 'ergonomic office chair' },
      { label: 'פינת אוכל', value: 'dining chair' },
      { label: 'בר', value: 'bar stool chair' },
      { label: 'גיימינג', value: 'gaming chair' },
      { label: 'חוץ / גינה', value: 'outdoor garden chair' },
    ],
  },
  {
    keywords: ['שולחן', 'desk', 'table'],
    question: 'איזה סוג שולחן?',
    options: [
      { label: 'שולחן עמידה', value: 'standing desk' },
      { label: 'שולחן מחשב', value: 'computer desk' },
      { label: 'שולחן משרדי', value: 'office desk' },
      { label: 'שולחן אוכל', value: 'dining table' },
      { label: 'שולחן ילדים', value: 'kids study desk' },
    ],
  },
  {
    keywords: ['מקלדת', 'keyboard'],
    question: 'איזה סוג מקלדת?',
    options: [
      { label: 'מכנית', value: 'mechanical keyboard' },
      { label: 'אלחוטית', value: 'wireless keyboard' },
      { label: 'ארגונומית', value: 'ergonomic split keyboard' },
      { label: 'גיימינג', value: 'gaming keyboard RGB' },
      { label: 'קומפקטית / 60%', value: 'compact 60% keyboard' },
    ],
  },
  {
    keywords: ['מסך', 'monitor'],
    question: 'לאיזה שימוש המסך?',
    options: [
      { label: 'עבודה משרדית', value: 'office monitor IPS' },
      { label: 'גיימינג', value: 'gaming monitor 144Hz' },
      { label: 'עיצוב / וידאו', value: 'color-accurate monitor 4K' },
      { label: 'אולטרה-רחב', value: 'ultrawide curved monitor' },
      { label: 'נייד', value: 'portable USB-C monitor' },
    ],
  },
  {
    keywords: ['אוזניות', 'headphones'],
    question: 'איזה סוג אוזניות?',
    options: [
      { label: 'מבטלות רעשים', value: 'noise cancelling headphones' },
      { label: 'אלחוטיות (אירבאדס)', value: 'wireless earbuds TWS' },
      { label: 'גיימינג', value: 'gaming headset with mic' },
      { label: 'סטודיו / מקצועיות', value: 'studio monitor headphones' },
      { label: 'ספורט / ריצה', value: 'sports wireless earbuds waterproof' },
    ],
  },
  {
    keywords: ['עכבר', 'mouse'],
    question: 'איזה סוג עכבר?',
    options: [
      { label: 'ארגונומי', value: 'ergonomic vertical mouse' },
      { label: 'גיימינג', value: 'gaming mouse' },
      { label: 'אלחוטי למשרד', value: 'wireless office mouse' },
      { label: 'טראקבול', value: 'trackball mouse' },
    ],
  },
  {
    keywords: ['לפטופ', 'מחשב נייד', 'laptop'],
    question: 'לאיזה שימוש המחשב הנייד?',
    options: [
      { label: 'פיתוח / עבודה', value: 'laptop for programming 16GB RAM' },
      { label: 'סטודנט / שימוש קל', value: 'lightweight student laptop' },
      { label: 'גיימינג', value: 'gaming laptop RTX' },
      { label: 'עריכת וידאו', value: 'laptop for video editing' },
      { label: 'תקציב נמוך', value: 'budget laptop under 2000 ILS' },
    ],
  },
  {
    keywords: ['מצלמה', 'camera'],
    question: 'איזה סוג מצלמה?',
    options: [
      { label: 'אבטחה', value: 'security camera WiFi' },
      { label: 'מירורלס', value: 'mirrorless camera' },
      { label: 'מצלמת רשת', value: 'webcam 1080p' },
      { label: 'אקשן', value: 'action camera waterproof' },
    ],
  },
  {
    keywords: ['מדפסת', 'printer'],
    question: 'איזה סוג מדפסת?',
    options: [
      { label: 'ביתית / הזרקת דיו', value: 'inkjet color printer' },
      { label: 'משרדית / לייזר', value: 'laser printer' },
      { label: 'מדפסת תמונות', value: 'photo printer' },
      { label: 'מדפסת תלת מימד', value: '3D printer' },
    ],
  },
  {
    keywords: ['תאורה', 'מנורה', 'light'],
    question: 'איזה סוג תאורה?',
    options: [
      { label: 'מנורת שולחן', value: 'LED desk lamp' },
      { label: 'תאורה חכמה', value: 'smart LED bulbs' },
      { label: 'טבעת אור', value: 'ring light for streaming' },
      { label: 'תקרה / חדר', value: 'LED ceiling light' },
    ],
  },
];

/**
 * Check if a query is generic enough to need clarification.
 * Returns a matching rule or null.
 */
export function findClarification(query) {
  const q = query.toLowerCase().trim();
  const wordCount = q.split(/\s+/).length;
  if (wordCount >= 3) return null;

  for (const rule of CLARIFICATION_RULES) {
    for (const kw of rule.keywords) {
      if (q.includes(kw.toLowerCase())) {
        return rule;
      }
    }
  }
  return null;
}
