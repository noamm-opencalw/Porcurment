from crewai import Agent, LLM

from src.config.settings import (
    CREWAI_CHEAP_MODEL,
    CREWAI_DEFAULT_MODEL,
    CREWAI_PREMIUM_MODEL,
    GEMINI_API_KEY,
)
from src.tools.deal_scraper import DealScraperTool
from src.tools.email_tool import EmailTool
from src.tools.price_comparator import PriceComparatorTool
from src.tools.web_search import WebSearchTool

# ----- LLM instances -----
llm_default = LLM(model=CREWAI_DEFAULT_MODEL, api_key=GEMINI_API_KEY)
llm_premium = LLM(model=CREWAI_PREMIUM_MODEL)
llm_cheap = LLM(model=CREWAI_CHEAP_MODEL)

# ----- Shared tool instances -----
_web_search = WebSearchTool()
_deal_scraper = DealScraperTool()
_price_comparator = PriceComparatorTool()


def create_product_specifier() -> Agent:
    return Agent(
        role="ארכיטקט מפרטי מוצרים לשוק הישראלי",
        goal=(
            "להמיר בקשת משתמש כללית למפרט טכני סופי הכולל דגם מדויק (Exact Model Name) ומק\"ט יצרן. "
            "עליך להפיק רשימה של 3-5 שאילתות יעילות לחיפוש בזאפ, KSP ו-Google Shopping Israel."
        ),
        backstory=(
            "אתה מומחה קטלוגים. אתה יודע שההבדל בין מחיר של 2,000 ש\"ח ל-4,000 ש\"ח "
            "נובע לרוב מתת-דגם (למשל נפח אחסון או סוג מעבד). המשימה שלך היא לוודא "
            "שהסוכנים הבאים בשרשרת יחפשו את אותו מוצר בדיוק ולא וריאציות זולות שלו."
        ),
        llm=llm_default,
        tools=[_web_search],
        memory=False,
        verbose=True,
        max_iter=6,
        allow_delegation=False,
    )


def create_deal_hunter() -> Agent:
    return Agent(
        role="חוקר שטח לאיתור מחירי אמת",
        goal=(
            "לאתר 5-10 הצעות מחיר עדכניות וזמינות במלאי מחנויות ישראליות. "
            "עבור כל הצעה, עליך להוציא: שם חנות, מחיר סופי בשקלים, וקישור ישיר לעמוד המוצר. "
            "חובה לוודא שהמחיר כולל מע\"מ."
        ),
        backstory=(
            "אתה 'קונה סמוי' קפדן. אתה לא מאמין למחירים שמופיעים בתקצירי חיפוש בגוגל "
            "כי הם לרוב לא מעודכנים. אתה משתמש ב-deal_scraper על דפי המוצר עצמם. "
            "אם המחיר בקישור לא תואם למחיר שמצאת בחיפוש — המחיר בתוך הקישור הוא הקובע. "
            "פסול עסקאות שנראות כמו יד שנייה או מחודש אלא אם התבקשת אחרת."
        ),
        llm=llm_default,
        tools=[_web_search, _deal_scraper],
        memory=False,
        verbose=True,
        max_iter=15,
        allow_delegation=False,
    )


def create_deal_analyst() -> Agent:
    return Agent(
        role="מנתח עסקאות ומעריך מוצרים",
        goal=(
            "נתח ודרג את העסקאות שנמצאו לפי ערך לקונה ישראלי פרטי. לכל עסקה, העריך: "
            "עלות כוללת אמיתית (כולל משלוח, מע״מ ומכס אם רלוונטי), "
            "אמינות המוכר, סיכון מקוריות המוצר, מדיניות החזרה, "
            "ויחס עלות-תועלת בשקלים. בחר את 3 העסקאות הטובות ביותר עם נימוק ברור."
        ),
        backstory=(
            "אתה יועץ קניות אישי מומחה בשוק הישראלי שעזר לאלפי צרכנים "
            "לחסוך כסף ברכישות חכמות. אתה יודע שהמחיר הזול ביותר לא תמיד הוא "
            "העסקה הטובה ביותר — אתה מתחשב במוניטין המוכר, זמן משלוח, "
            "אחריות בישראל, ועלויות נסתרות. כבר נתקלת בעסקאות-טוב-מדי-מכדי-להיות-אמיתיות "
            "ולכן תמיד מאמת לגיטימיות. ההערכות שלך מבוססות נתונים."
        ),
        llm=llm_premium,
        tools=[_web_search, _price_comparator],
        memory=False,
        verbose=True,
        max_iter=8,
        allow_delegation=False,
    )


def create_email_agent() -> Agent:
    return Agent(
        role="שליח דוחות עסקאות",
        goal=(
            "שלח דוחות סיכום עסקאות במייל למשתמש. "
            "תקשורת מקצועית ותמציתית בעברית."
        ),
        backstory=(
            "אתה עוזר אישי שיודע לכתוב מיילים ברורים ומקצועיים. "
            "אתה מפרמט את דוחות העסקאות בצורה קריאה ונעימה, "
            "עם כל הפרטים החשובים: מחיר, מוכר, קישור, טלפון."
        ),
        llm=llm_cheap,
        tools=[EmailTool()],
        memory=False,
        verbose=True,
        max_iter=5,
        allow_delegation=False,
    )


def create_procurement_lead() -> Agent:
    return Agent(
        role="מומחה המלצות רכש",
        goal=(
            "בדוק את 3 העסקאות המובילות מהמנתח, ודא שהן עומדות בסטנדרטים, "
            "והפק דוח המלצות סופי עם החלטות ברורות: קנה / נהל מו״מ / דלג. "
            "ודא שכל תוצאה כוללת: תיאור, קישור, טלפון, מחיר, והסבר מפורט."
        ),
        backstory=(
            "אתה יועץ צרכנות מומחה שחושב מעבר למחיר: עלות כוללת, "
            "אמינות המוכר, אחריות, ומדיניות החזרה. אתה מציג ממצאים "
            "בצורה ברורה ופרקטית. כל המלצה כוללת הערכת סיכון "
            "ואסטרטגיית משא ומתן."
        ),
        llm=llm_premium,
        tools=[_web_search, _price_comparator],
        memory=False,
        verbose=True,
        max_iter=6,
        allow_delegation=True,
    )
