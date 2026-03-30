"""Telegram bot for DealFinder — search for deals via Telegram."""

import json
import logging
import os
import threading

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

try:
    from src.db.models import Deal, SearchQuery, get_session, init_db
    from src.flows.main_flow import ProcurementFlow
    HAS_CREWAI = True
except ImportError as e:
    logging.warning(f"Could not import project modules: {e}")
    HAS_CREWAI = False
    ProcurementFlow = None

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "👋 ברוכים הבאים ל-DealFinder!\n\n"
        "שלחו לי שם של מוצר ואמצא לכם את העסקאות הטובות ביותר בישראל.\n\n"
        "📝 דוגמה: אוזניות Sony WH-1000XM5\n\n"
        "פקודות:\n"
        "/search <מוצר> — חיפוש עסקאות\n"
        "/history — היסטוריית חיפושים\n"
        "/help — עזרה"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await update.message.reply_text(
        "🔍 *DealFinder Bot*\n\n"
        "פשוט שלחו שם מוצר וה-AI ימצא לכם את העסקאות הטובות ביותר!\n\n"
        "*פקודות:*\n"
        "/search <מוצר> — חיפוש עסקאות\n"
        "/history — 10 חיפושים אחרונים\n"
        "/help — הודעה זו\n\n"
        "💡 *טיפ:* ככל שתהיו יותר ספציפיים, התוצאות יהיו טובות יותר.",
        parse_mode="Markdown",
    )


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history command."""
    if not HAS_CREWAI:
        await update.message.reply_text("⚠️ מודול החיפוש לא זמין כרגע.")
        return
    init_db()
    session = get_session()
    try:
        searches = (
            session.query(SearchQuery)
            .order_by(SearchQuery.started_at.desc())
            .limit(10)
            .all()
        )
        if not searches:
            await update.message.reply_text("📭 אין חיפושים קודמים.")
            return

        lines = ["📋 *חיפושים אחרונים:*\n"]
        for s in searches:
            status_icon = "✅" if s.status == "completed" else "⏳" if s.status == "running" else "❌"
            deals_info = f" — {s.deals_found} עסקאות" if s.deals_found else ""
            lines.append(f"{status_icon} {s.product_query}{deals_info}")

        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    finally:
        session.close()


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /search command."""
    query = " ".join(context.args) if context.args else ""
    if not query:
        await update.message.reply_text("⚠️ נא לציין מוצר לחיפוש.\nדוגמה: /search אוזניות אלחוטיות")
        return
    await _run_search(update, query)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle plain text messages as search queries."""
    query = update.message.text.strip()
    if not query:
        return
    await _run_search(update, query)


async def _run_search(update: Update, query: str):
    """Run procurement search and send results."""
    if not HAS_CREWAI:
        await update.message.reply_text(
            "⚠️ מודול החיפוש (crewai) לא מותקן כרגע.\n"
            "התקינו עם: pip install crewai"
        )
        return

    msg = await update.message.reply_text(
        f"🔍 מחפש עסקאות עבור: *{query}*\n\n"
        "⏳ זה עשוי לקחת כמה דקות...",
        parse_mode="Markdown",
    )

    try:
        flow = ProcurementFlow(query)
        result = flow.kickoff()
        raw = str(result)

        # Parse JSON
        parsed = _parse_json(raw)

        if parsed and parsed.get("deals"):
            deals = parsed["deals"]
            summary = parsed.get("recommendation_summary", "")

            # Send summary
            response = f"✅ *נמצאו {len(deals)} עסקאות עבור: {query}*\n\n"
            if summary:
                response += f"📊 {summary}\n\n"

            await msg.edit_text(response, parse_mode="Markdown")

            # Send each deal as a separate message
            for deal in deals[:5]:  # Top 5 deals
                deal_text = _format_deal(deal)
                await update.message.reply_text(deal_text, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            await msg.edit_text(
                f"😔 לא הצלחתי למצוא עסקאות עבור: {query}\n"
                "נסו לחפש עם מילים אחרות."
            )

    except Exception as e:
        logger.error(f"Search error: {e}")
        await msg.edit_text(
            f"❌ שגיאה בחיפוש: {query}\n\n{str(e)[:200]}"
        )


def _format_deal(deal: dict) -> str:
    """Format a deal for Telegram message."""
    rank = deal.get("rank", "?")
    title = deal.get("title", "ללא שם")
    price = deal.get("price", deal.get("price_numeric", "לא זמין"))
    if isinstance(price, (int, float)):
        price = f"₪{price:,.2f}"
    seller = deal.get("seller", "לא ידוע")
    url = deal.get("url", "")
    verdict = deal.get("verdict", "")
    explanation = deal.get("explanation", "")
    risk = deal.get("risk_level", "")
    score = deal.get("total_score", "")
    negotiation = deal.get("negotiation_strategy", "")

    verdict_icon = {"BUY": "🟢", "NEGOTIATE": "🟡", "PASS": "🔴"}.get(verdict, "⚪")

    lines = [f"*#{rank} {title}*\n"]
    lines.append(f"💰 מחיר: {price}")
    lines.append(f"🏪 מוכר: {seller}")
    if score:
        lines.append(f"⭐ ציון: {score}/100")
    if verdict:
        lines.append(f"{verdict_icon} המלצה: {verdict}")
    if risk:
        lines.append(f"⚠️ סיכון: {risk}")
    if explanation:
        lines.append(f"\n📝 {explanation[:200]}")
    if negotiation:
        lines.append(f"\n💡 מו\"מ: {negotiation[:150]}")
    if url:
        lines.append(f"\n🔗 [קישור לעסקה]({url})")

    return "\n".join(lines)


def _parse_json(raw: str) -> dict | None:
    """Try to extract JSON from raw output."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(raw[start:end])
        except json.JSONDecodeError:
            pass
    return None


def main():
    """Start the Telegram bot."""
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set in .env")
        return

    if HAS_CREWAI:
        init_db()

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 DealFinder Telegram bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
