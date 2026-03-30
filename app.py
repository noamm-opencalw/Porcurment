"""Porcurment — Flask Web App for AI Procurement Deal Finding."""

import csv
import io
import json
from datetime import datetime, timezone

from flask import Flask, Response, redirect, render_template, request, url_for

from src.db.models import Deal, SearchQuery, SearchResult, get_session, init_db
from src.flows.main_flow import ProcurementFlow

app = Flask(__name__)


@app.before_request
def ensure_db():
    """Initialize DB tables on first request."""
    init_db()


# ---- Routes ----


@app.route("/")
def home():
    """Home page — product search."""
    return render_template("home.html", active_page="home")


@app.route("/search", methods=["POST"])
def search():
    """Handle search form submission — run the procurement flow."""
    product_query = request.form.get("product_query", "").strip()
    if not product_query:
        return redirect(url_for("home"))

    # Run the flow
    try:
        flow = ProcurementFlow(product_query)
        result = flow.kickoff()
        raw = str(result)

        # Parse JSON from output
        parsed = _parse_json(raw)

        if parsed:
            # Get search_id from the flow state
            search_id = flow.state.get("search_id")
            return render_template(
                "results.html",
                active_page="home",
                product_query=product_query,
                summary=parsed.get("recommendation_summary", ""),
                deals=parsed.get("deals", []),
                search_id=search_id,
                error=None,
            )
        else:
            return render_template(
                "results.html",
                active_page="home",
                product_query=product_query,
                summary=None,
                deals=[],
                search_id=None,
                error="לא ניתן לעבד את תוצאות ה-AI. התגובה הגולמית נשמרה.",
            )

    except Exception as e:
        return render_template(
            "results.html",
            active_page="home",
            product_query=product_query,
            summary=None,
            deals=[],
            search_id=None,
            error=str(e),
        )


@app.route("/results/<int:search_id>")
def view_results(search_id):
    """View results for a past search from DB."""
    session = get_session()
    try:
        search = session.get(SearchQuery, search_id)
        if not search:
            return redirect(url_for("history"))

        deals = (
            session.query(Deal)
            .filter(Deal.search_id == search_id)
            .order_by(Deal.rank)
            .all()
        )

        search_result = (
            session.query(SearchResult)
            .filter(SearchResult.search_id == search_id)
            .first()
        )

        deal_list = [
            {
                "rank": d.rank or i + 1,
                "title": d.title,
                "description": d.description,
                "price": f"₪{d.price:,.2f}" if d.price else "לא זמין",
                "price_numeric": d.price,
                "url": d.url,
                "phone": d.phone,
                "seller": d.seller,
                "verdict": d.verdict,
                "explanation": d.explanation,
                "risk_level": d.risk_level,
                "risk_notes": d.risk_notes,
                "negotiation_strategy": d.negotiation_strategy,
                "score_breakdown": d.score_breakdown or {},
                "total_score": d.total_score,
            }
            for i, d in enumerate(deals)
        ]

        return render_template(
            "results.html",
            active_page="history",
            product_query=search.product_query,
            summary=search_result.recommendation_summary if search_result else None,
            deals=deal_list,
            search_id=search_id,
            error=None if search.status == "completed" else "החיפוש לא הושלם בהצלחה.",
        )
    finally:
        session.close()


@app.route("/history")
def history():
    """History page — past searches."""
    session = get_session()
    try:
        searches = (
            session.query(SearchQuery)
            .order_by(SearchQuery.started_at.desc())
            .limit(50)
            .all()
        )
        return render_template("history.html", active_page="history", searches=searches)
    finally:
        session.close()


@app.route("/export/<int:search_id>")
def export_csv(search_id):
    """Export deals as CSV."""
    session = get_session()
    try:
        search = session.get(SearchQuery, search_id)
        deals = (
            session.query(Deal)
            .filter(Deal.search_id == search_id)
            .order_by(Deal.rank)
            .all()
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "דירוג", "שם מוצר", "מחיר", "מוכר", "קישור", "טלפון",
            "המלצה", "ציון", "סיכון", "הסבר",
        ])
        for d in deals:
            writer.writerow([
                d.rank,
                d.title,
                f"₪{d.price:.2f}" if d.price else "לא זמין",
                d.seller,
                d.url,
                d.phone,
                d.verdict,
                d.total_score,
                d.risk_level,
                d.explanation,
            ])

        filename = f"porcurment_{search.product_query.replace(' ', '_')}.csv" if search else "porcurment_deals.csv"

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    finally:
        session.close()


# ---- Helpers ----


def _parse_json(raw: str) -> dict | None:
    """Try to extract JSON from raw output."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Try extracting JSON block
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(raw[start:end])
        except json.JSONDecodeError:
            pass

    return None


# ---- Run ----

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
