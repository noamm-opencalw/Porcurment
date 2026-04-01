from crewai import Agent, Task


def create_product_specification_task(agent: Agent, product_query: str) -> Task:
    return Task(
        description=f"""חקור את המוצר "{product_query}" וצור מפרט חיפוש מפורט:

1. השתמש ב-web_search כדי לחקור את קטגוריית המוצר ולמצוא דגמים פופולריים.
2. זהה מספרי דגם/SKU ספציפיים הזמינים בישראל.
3. הערך טווח מחירים ריאלי לשוק הישראלי.
4. זהה 3-4 מפרטים מרכזיים שחשוב לכלול בחיפוש.
5. צור 5 שאילתות חיפוש ממוקדות:
   - site:zap.co.il {{product}}
   - site:ksp.co.il {{product}}
   - site:ivory.co.il {{product}}
   - {{product}} מחיר השוואה ישראל
   - {{product}} cheapest Israel buy""",
        expected_output="""אובייקט JSON בלבד:
{{
  "specific_query": "<מונחי חיפוש מדויקים בעברית ואנגלית כולל מותג + דגם + מפרט מרכזי>",
  "model_numbers": ["<מספר דגם 1>", "<מספר דגם 2>"],
  "price_range_ils": {{"min": <מינימום>, "max": <מקסימום>}},
  "key_specs": ["<מפרט 1>", "<מפרט 2>", "<מפרט 3>"],
  "search_queries": [
    "site:zap.co.il <product>",
    "site:ksp.co.il <product>",
    "site:ivory.co.il <product>",
    "<product> מחיר השוואה ישראל",
    "<product> cheapest Israel buy"
  ]
}}

פלט אך ורק JSON תקין, בלי טקסט אחר.""",
        agent=agent,
    )


def create_broad_search_task(
    agent: Agent,
    product_query: str,
    include_international: bool = False,
    search_queries: list[str] | None = None,
) -> Task:
    if include_international:
        channels = """3. חפש במספר ערוצים בעדיפות לזמינות בישראל:
   - קמעונאים ישראליים: KSP, Ivory, Bug, Zap, iDigital, מחסני חשמל
   - אתרים בינלאומיים עם משלוח לישראל: Amazon, eBay, AliExpress
   - אתרי השוואת מחירים ומצברי עסקאות (Zap, Pricez)
4. כלול עסקאות גם ממקורות ישראליים וגם בינלאומיים עם משלוח לישראל."""
    else:
        channels = """3. חפש רק בחנויות ואתרים ישראליים:
   - קמעונאים ישראליים: KSP, Ivory, Bug, Zap, iDigital, מחסני חשמל
   - Amazon.co.il
   - אתרי השוואת מחירים (Zap, Pricez)
4. התמקד אך ורק בעסקאות ממקורות ישראליים. אל תחפש באתרים בינלאומיים."""

    if search_queries:
        queries_block = "1. הרץ את שאילתות החיפוש הממוקדות הבאות:\n" + "\n".join(
            f'   - "{q}"' for q in search_queries
        )
    else:
        queries_block = f"""1. הרץ שאילתות חיפוש ממוקדות לאתרים ספציפיים:
   - "site:zap.co.il {product_query}"
   - "site:ksp.co.il {product_query}"
   - "site:ivory.co.il {product_query}"
   - "{product_query} השוואת מחירים"
   - "{product_query} cheapest Israel" """

    return Task(
        description=f"""חפש עסקאות על המוצר הבא הזמין בישראל: {product_query}

{queries_block}
2. לכל תוצאה מבטיחה, השתמש ב-deal_scraper כדי לחלץ:
   שם מוצר, מחיר, URL, שם מוכר, מספר טלפון, ותיאור.
{channels}
5. אסוף לפחות 10 עסקאות שונות עם מחירים מאומתים.
6. לכל עסקה, ציין את סוג המקור: retail, marketplace, או price_comparison.
7. מחירים צריכים להיות ב-₪ (שקלים) כשזמין, או בדולרים עם ציון משלוח לישראל.
8. לכל שאילתת חיפוש, חלץ רק URLs שהם דפי מוצר ישירים (המכילים את המוצר, מחיר וכפתור הוספה לסל).
   דחה דפי קטגוריה, בלוגים ודפי תוצאות חיפוש.

חשוב: כלול רק עסקאות שזמינות כעת וניתנות לרכישה/משלוח בישראל. דלג על עסקאות שפג תוקפן.""",
        expected_output="""רשימת JSON של 10+ עסקאות. לכל עסקה חייב להיות:
- title: שם המוצר/כותרת
- price: מחיר מספרי (למשל 299.90)
- currency: "ILS" או "USD" לבינלאומי
- url: קישור ישיר לעסקה
- seller: שם החנות/מוכר
- phone: מספר טלפון ליצירת קשר (או "N/A")
- description: תיאור מוצר של 2-3 משפטים
- source_type: "retail" | "marketplace" | "price_comparison"
- shipping_info: עלות משלוח, "חינם", או "לא ידוע"

CRITICAL: Every url field MUST be a direct link to the product page on the retailer's website. URLs containing 'google.com/search', '/search?q=', or any search engine results page are STRICTLY FORBIDDEN. If you cannot find a direct product URL, omit that deal entirely.

פלט אך ורק את מערך ה-JSON, בלי טקסט אחר.""",
        agent=agent,
    )


def create_deal_enrichment_task(agent: Agent) -> Task:
    return Task(
        description="""לכל אחת מ-10 העסקאות שנמצאו בחיפוש הקודם:

1. בקר ב-URL של העסקה באמצעות deal_scraper וחלץ פרטים נוספים אם חסרים.
2. ודא שהמחיר עדכני (לא פג תוקף או אזל מהמלאי).
3. חפש מספרי טלפון בדף יצירת הקשר של המוכר אם חסר.
4. ציין קודי קופון או מבצעים פעילים.
5. סמן עסקאות שנראות חשודות (זול מדי, מוכר לא ידוע, ללא פרטי קשר).

חשוב: שמור על כל העסקאות גם אם חסרים פרטים — סמן אותן כלא מאומתות.""",
        expected_output="""רשימת JSON מעודכנת עם נתוני עסקאות מועשרים. כל עסקה כוללת כעת:
- כל השדות מהחיפוש הרחב
- verified: true/false (האם המחיר מאושר כעדכני?)
- coupon_codes: קודי קופון פעילים (או null)
- suspicious_flags: רשימת חשדות (או רשימה ריקה [])

פלט אך ורק את מערך ה-JSON, בלי טקסט אחר.""",
        agent=agent,
    )


def create_deal_analysis_task(agent: Agent, product_query: str) -> Task:
    return Task(
        description=f"""נתח ודרג את כל העסקאות שנמצאו עבור "{product_query}" עבור קונה ישראלי פרטי:

1. השתמש בכלי price_comparator כדי להשוות את כל מחירי העסקאות ולמצוא את ממוצע השוק בישראל.
2. דרג כל עסקה ב-5 קריטריונים (1-10 לכל אחד):
   - תחרותיות מחיר (מול ממוצע השוק הישראלי מהמשווה)
   - אמינות ספק (מותג ידוע? מוכר מבוסס בישראל? פרטי קשר זמינים?)
   - עלות כוללת (כולל משלוח לישראל, מע״מ, מכס אם רלוונטי)
   - מקוריות מוצר (מוצר מקורי? משווק מורשה בישראל? דגלים חשודים?)
   - הגנת קונה (ציות לחוק הגנת הצרכן הישראלי, מדיניות החזרה, אחריות תקפה בישראל, אבטחת תשלום)
3. חשב ציון כולל משוקלל:
   מחיר: 30%, אמינות: 25%, עלות כוללת: 20%, מקוריות: 15%, הגנה: 10%
4. דרג את כל העסקאות לפי ציון כולל (הגבוה ביותר קודם).
5. בחר את 3 העסקאות המובילות.
6. לכל עסקה מובילה, כתוב הסבר של 2-3 משפטים למה זו עסקה טובה לצרכן ישראלי.
7. כלול טיפ משא ומתן לכל עסקה.

חשוב: קח בחשבון suspicious_flags בדירוג. עסקאות עם הרבה דגלים אדומים צריכות לקבל ציון נמוך.
לעסקאות בינלאומיות, חשב את העלות הכוללת בישראל (מחיר + משלוח + מכס + מע״מ).""",
        expected_output="""אובייקט JSON עם:
- "all_deals_scored": רשימת כל העסקאות עם הציונים שלהן
- "top_3": רשימת 3 העסקאות הטובות ביותר, כל אחת מכילה:
  - title, price, url, seller, phone, description
  - total_score (0-100)
  - score_breakdown: {"price": X, "reliability": X, "total_cost": X, "authenticity": X, "protection": X}
  - explanation: למה העסקה הזו בולטת (2-3 משפטים)
  - negotiation_tip: איך אפשר לקבל מחיר טוב יותר

פלט אך ורק JSON תקין, בלי טקסט אחר.""",
        agent=agent,
    )


def create_final_recommendation_task(agent: Agent, product_query: str) -> Task:
    return Task(
        description=f"""בדוק את 3 העסקאות המובילות של המנתח עבור "{product_query}" והפק המלצה סופית:

1. ודא שכל עסקה עומדת בסטנדרטים:
   - יש URL עובד
   - יש מחיר ניתן לאימות
   - המוכר ניתן לזיהוי
2. הקצה המלצה לכל עסקה: קנה / נהל מו״מ / דלג
   - קנה: עסקה מצוינת, לרכוש מיד
   - נהל מו״מ: פוטנציאל טוב, כדאי לנסות להוריד מחיר קודם
   - דלג: לא מומלץ למרות שנמצא ב-3 המובילים
3. הוסף הערכת סיכון לכל עסקה (נמוך/בינוני/גבוה + הערות).
4. כתוב סיכום מנהלים של 2-3 משפטים על תוצאות החיפוש הכוללות.
5. ודא שכל השדות הנדרשים קיימים לתצוגת ממשק:
   תיאור, קישור, טלפון, מחיר, והסבר.

חשוב: הפלט חייב להיות JSON תקין בדיוק לפי הסכמה למטה.""",
        expected_output="""אובייקט JSON:
{{
  "product_searched": "<שאילתת המוצר>",
  "recommendation_summary": "<סיכום מנהלים של 2-3 משפטים>",
  "deals": [
    {{
      "rank": 1,
      "title": "<שם מוצר>",
      "description": "<תיאור מלא>",
      "price": "<מחיר מפורמט למשל ₪299.90>",
      "price_numeric": 299.90,
      "url": "<קישור לעסקה>",
      "phone": "<טלפון מוכר או N/A>",
      "seller": "<שם מוכר>",
      "verdict": "BUY",
      "explanation": "<למה זו עסקה טובה, 2-3 משפטים>",
      "risk_level": "low",
      "risk_notes": "<חששות ספציפיים או 'אין'>",
      "negotiation_strategy": "<גישה מוצעת>",
      "score_breakdown": {{"price": 9, "reliability": 8, "total_cost": 8, "authenticity": 9, "protection": 7}},
      "total_score": 85
    }}
  ]
}}

פלט אך ורק JSON תקין, בלי טקסט אחר.""",
        agent=agent,
    )


def create_send_report_task(
    agent: Agent, product_query: str, recipient_email: str
) -> Task:
    return Task(
        description=f"""שלח את 3 המלצות העסקאות המובילות עבור "{product_query}" במייל:

1. פרמט את העסקאות לאימייל HTML מקצועי עם:
   - נושא: "דוח עסקאות: ההמלצות המובילות עבור {product_query}"
   - פסקת פתיחה קצרה
   - פריסת כרטיסים לכל עסקה: שם, מחיר, מוכר, קישור, טלפון
   - הסבר והמלצה לכל עסקה
   - כותרת תחתית "נוצר על ידי פורקורמנט AI"
2. שלח ל: {recipient_email}""",
        expected_output="JSON אישור עם סטטוס הצלחה ומזהה הודעה.",
        agent=agent,
    )


def create_search_emails_task(agent: Agent, product_query: str) -> Task:
    return Task(
        description=f"""בדוק תיבת מייל להצעות מחיר מספקים הקשורות ל-"{product_query}":

1. חפש מיילים אחרונים עם שם המוצר בנושא.
2. חלץ תמחור, תנאים ופרטי קשר מכל מייל שנמצא.
3. החזר נתונים מובנים לכל הצעת מחיר.""",
        expected_output="""רשימת JSON של הצעות מחיר מספקים:
[{{"from": "...", "subject": "...", "price": "...", "terms": "...", "contact": "..."}}]""",
        agent=agent,
    )
