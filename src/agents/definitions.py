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
            "קבל שאילתת מוצר גולמית מהמשתמש והפוך אותה למפרט חיפוש מדויק. "
            "חקור את קטגוריית המוצר באינטרנט, זהה את הדגמים המובילים בשוק הישראלי, "
            "טווח מחירים ריאלי, ומפרט טכני חיוני. "
            "הפק רשימת שאילתות חיפוש ממוקדות שכוללות site: operators לאתרים ישראליים ספציפיים "
            "(zap.co.il, ksp.co.il, ivory.co.il) כדי להבטיח תוצאות רלוונטיות עם מחירים אמיתיים."
        ),
        backstory=(
            "אתה אנליסט מוצרים בכיר עם 8 שנות ניסיון בשוק האלקטרוניקה והצריכה הישראלי. "
            "אתה מכיר לעומק את ההבדלים בין דגמים, יודע אילו מותגים נמכרים בארץ דרך יבוא מקביל "
            "לעומת יבוא רשמי, ומבין את פערי המחירים בין חנויות. "
            "למדת מניסיון שחיפוש גנרי כמו 'מקלדת אלחוטית' מחזיר תוצאות חסרות ערך — "
            "אבל חיפוש ממוקד כמו 'Logitech MX Keys S site:ksp.co.il' מחזיר את דף המוצר המדויק עם המחיר. "
            "אתה תמיד מייצר 5 שאילתות חיפוש: 3 ממוקדות לאתרים ישראליים ספציפיים ו-2 כלליות."
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
