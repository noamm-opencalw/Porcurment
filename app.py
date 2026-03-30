"""Porcurment — Flask Web App for AI Procurement Deal Finding."""

import csv
import io
import json
from datetime import datetime, timezone

from flask import Flask, Response, jsonify, redirect, request

from src.db.models import Deal, SearchQuery, SearchResult, get_session, init_db
from src.flows.main_flow import ProcurementFlow

app = Flask(__name__)


# ---- CORS (allow SPA from docs/ to call API) ----

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.before_request
def ensure_db():
    """Initialize DB tables on first request."""
    init_db()


# ---- JSON API routes (for SPA) ----


@app.route("/api/search", methods=["POST", "OPTIONS"])
def api_search():
    """Run procurement search and return JSON results."""
    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json(force=True, silent=True) or {}
    product_query = data.get("product_query", "").strip()
    include_international = data.get("include_international", False)

    if not product_query:
        return jsonify({"error": "missing product_query"}), 400

    try:
        flow = ProcurementFlow(product_query, include_international=include_international)
        result = flow.kickoff()
        raw = str(result)
        parsed = _parse_json(raw)

        search_id = flow.state.get("search_id")

        if parsed:
            return jsonify({
                "search_id": search_id,
                "product_query": product_query,
                "recommendation_summary": parsed.get("recommendation_summary", ""),
                "deals": parsed.get("deals", []),
            })
        else:
            return jsonify({
                "search_id": search_id,
                "product_query": product_query,
                "error": "לא ניתן לעבד את תוצאות ה-AI.",
                "deals": [],
            })

    except Exception as e:
        return jsonify({"error": str(e), "deals": []}), 500


@app.route("/api/history")
def api_history():
    """Return search history as JSON."""
    session = get_session()
    try:
        searches = (
            session.query(SearchQuery)
            .order_by(SearchQuery.started_at.desc())
            .limit(50)
            .all()
        )
        return jsonify([
            {
                "id": s.id,
                "product_query": s.product_query,
                "status": s.status,
                "deals_found": s.deals_found or 0,
                "include_international": getattr(s, "include_international", False),
                "started_at": s.started_at.isoformat() if s.started_at else None,
            }
            for s in searches
        ])
    finally:
        session.close()


@app.route("/api/results/<int:search_id>")
def api_results(search_id):
    """Return deal results for a search as JSON."""
    session = get_session()
    try:
        search = session.get(SearchQuery, search_id)
        if not search:
            return jsonify({"error": "search not found"}), 404

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

        return jsonify({
            "search_id": search_id,
            "product_query": search.product_query,
            "status": search.status,
            "recommendation_summary": search_result.recommendation_summary if search_result else "",
            "deals": deal_list,
        })
    finally:
        session.close()


# ---- Redirect non-API routes to GitHub Pages SPA ----

FRONTEND_URL = "https://noamm-opencalw.github.io/Porcurment"


@app.route("/")
def home():
    return redirect(FRONTEND_URL)


@app.route("/search")
@app.route("/search", methods=["POST"])
def search():
    return redirect(FRONTEND_URL)


@app.route("/results/<int:search_id>")
def view_results(search_id):
    return redirect(f"{FRONTEND_URL}/#/results/{search_id}")


@app.route("/history")
def history():
    return redirect(f"{FRONTEND_URL}/#/history")


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
    app.run(debug=True, host="0.0.0.0", port=8080)
