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
        role="מומחה מפרט מוצרים",
        goal=(
            "קבל שאילתת מוצר כללית והפוך אותה למפרט חיפוש ספציפי ומדויק. "
            "חקור את קטגוריית המוצר, זהה דגמים מובילים ומקובלים בישראל, "
            "ופק רשימת שאילתות חיפוש ממוקדות לאתרי קניות ישראליים."
        ),
        backstory=(
            "אתה מומחה לניתוח מוצרים ומפרטים טכניים. אתה יודע איך לחקור "
            "קטגוריית מוצר, לזהות את הדגמים הפופולריים בשוק הישראלי, "
            "ולהמיר שאילתה כללית לחיפוש ספציפי שיניב תוצאות מדויקות "
            "באתרים כמו זאפ, KSP ו-Ivory."
        ),
        llm=llm_cheap,
        tools=[_web_search],
        memory=False,
        verbose=True,
        max_iter=6,
        allow_delegation=False,
    )


def create_deal_hunter() -> Agent:
    return Agent(
        role="מומחה איתור עסקאות",
        goal=(
            "חפש באינטרנט באופן יסודי כדי למצוא את 10 העסקאות הטובות ביותר עבור מוצר נתון "
            "הזמין בישראל. השתמש בשאילתות חיפוש מרובות, וריאציות ומקורות שונים. "
            "חפש בחנויות ישראליות (KSP, Ivory, Bug, Zap, iDigital, מחסני חשמל, Amazon.co.il) "
            "ובאתרי השוואת מחירים (Zap, Pricez). "
            "התמקד במציאת עסקאות אמיתיות וזמינות כעת עם מחירים מאומתים בשקלים."
        ),
        backstory=(
            "אתה צרכן חכם ומנוסה שמכיר את השוק הישראלי לעומק. אתה יודע לחפש "
            "לפי מק״ט יצרן, לבדוק אתרי השוואת מחירים כמו זאפ ופרייסז, להשוות בין "
            "משווקים מורשים בישראל, ולתזמן רכישות סביב מבצעים. אתה מחפש בצורה "
            "שיטתית — קודם מקורות ישראליים — ותמיד מתחשב במשלוח, מע״מ ועלויות נלוות."
        ),
        llm=llm_default,
        tools=[_web_search, _deal_scraper],
        memory=False,
        verbose=True,
        max_iter=12,
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
