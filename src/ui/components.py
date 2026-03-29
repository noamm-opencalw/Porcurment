"""Streamlit UI components for Porcurment — deal cards, styling, and layout helpers."""

import streamlit as st


def inject_custom_css():
    """Inject custom CSS for the fancy UI."""
    st.markdown(
        """
    <style>
    /* Main theme */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }

    /* Search header */
    .search-header {
        text-align: center;
        padding: 2rem 0 1rem;
    }
    .search-header h1 {
        font-size: 3rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }
    .search-header p {
        color: #a0a0b0;
        font-size: 1.1rem;
    }

    /* Deal cards */
    .deal-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .deal-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.3);
    }

    /* Rank badges */
    .rank-badge {
        display: inline-block;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        text-align: center;
        line-height: 36px;
        font-weight: 800;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    .rank-1 { background: linear-gradient(135deg, #f5af19, #f12711); color: white; }
    .rank-2 { background: linear-gradient(135deg, #c0c0c0, #8e8e8e); color: white; }
    .rank-3 { background: linear-gradient(135deg, #cd7f32, #8b5e3c); color: white; }

    /* Verdict badges */
    .verdict-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .verdict-buy { background: #10b981; color: white; }
    .verdict-negotiate { background: #f59e0b; color: #1a1a2e; }
    .verdict-pass { background: #ef4444; color: white; }

    /* Risk indicator */
    .risk-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .risk-low { background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }
    .risk-medium { background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid #f59e0b; }
    .risk-high { background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }

    /* Price tag */
    .price-tag {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #10b981, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
    }

    /* Score bar */
    .score-container {
        display: flex;
        gap: 4px;
        margin: 0.5rem 0;
    }
    .score-segment {
        height: 6px;
        border-radius: 3px;
        flex: 1;
    }

    /* Summary card */
    .summary-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15));
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin: 1rem 0 2rem;
    }
    .summary-card p {
        color: #e0e0f0;
        font-size: 1.05rem;
        line-height: 1.6;
    }

    /* Progress animation */
    .progress-stage {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0;
        color: #a0a0b0;
    }
    .progress-stage.active {
        color: #667eea;
        font-weight: 600;
    }
    .progress-stage.done {
        color: #10b981;
    }

    /* History sidebar */
    .history-item {
        padding: 0.5rem 0.75rem;
        border-radius: 8px;
        margin-bottom: 0.25rem;
        cursor: pointer;
        color: #c0c0d0;
        font-size: 0.9rem;
    }
    .history-item:hover {
        background: rgba(255, 255, 255, 0.05);
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4) !important;
    }

    /* Contact links */
    .contact-link {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
    }
    .contact-link:hover {
        text-decoration: underline;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def render_search_header():
    """Render the main search header."""
    st.markdown(
        """
    <div class="search-header">
        <h1>Porcurment</h1>
        <p>AI-Powered Procurement Deal Finder</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_summary_card(summary: str):
    """Render the executive summary card."""
    st.markdown(
        f"""
    <div class="summary-card">
        <p><strong>Executive Summary</strong></p>
        <p>{summary}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_deal_card(deal: dict, rank: int):
    """Render a single deal card with all details."""
    # Determine CSS classes
    rank_class = f"rank-{rank}" if rank <= 3 else ""
    verdict = deal.get("verdict", "PASS").upper()
    verdict_class = f"verdict-{verdict.lower()}"
    risk = deal.get("risk_level", "medium").lower()
    risk_class = f"risk-{risk}"

    price_display = deal.get("price", "N/A")
    if isinstance(price_display, (int, float)):
        price_display = f"${price_display:,.2f}"
    elif isinstance(price_display, str) and not price_display.startswith("$"):
        try:
            price_display = f"${float(price_display):,.2f}"
        except (ValueError, TypeError):
            pass

    phone = deal.get("phone", "N/A")
    phone_html = (
        f'<a href="tel:{phone}" class="contact-link">{phone}</a>'
        if phone and phone != "N/A"
        else "N/A"
    )

    url = deal.get("url", "#")
    score = deal.get("total_score", 0)

    # Score breakdown bars
    breakdown = deal.get("score_breakdown", {})
    score_bars = ""
    colors = {
        "price": "#10b981",
        "reliability": "#667eea",
        "total_cost": "#f59e0b",
        "authenticity": "#764ba2",
        "protection": "#ef4444",
    }
    for key, color in colors.items():
        val = breakdown.get(key, 5)
        width = val * 10
        score_bars += f'<div class="score-segment" style="background: {color}; width: {width}%; opacity: 0.8;" title="{key}: {val}/10"></div>'

    st.markdown(
        f"""
    <div class="deal-card">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <span class="rank-badge {rank_class}">#{rank}</span>
                <span class="verdict-badge {verdict_class}" style="margin-left: 8px;">{verdict}</span>
                <span class="risk-badge {risk_class}" style="margin-left: 8px;">Risk: {risk}</span>
            </div>
            <div style="text-align: right;">
                <div class="price-tag">{price_display}</div>
            </div>
        </div>

        <h3 style="margin: 0.75rem 0 0.25rem; color: #f0f0ff; font-size: 1.2rem;">{deal.get('title', 'Unknown Product')}</h3>
        <p style="color: #b0b0c0; font-size: 0.9rem; margin-bottom: 0.75rem;">{deal.get('seller', 'Unknown Seller')}</p>

        <p style="color: #d0d0e0; font-size: 0.95rem; line-height: 1.5;">{deal.get('description', 'No description available')}</p>

        <div style="background: rgba(102, 126, 234, 0.1); border-radius: 10px; padding: 1rem; margin: 0.75rem 0;">
            <p style="color: #e0e0f0; font-size: 0.95rem; margin: 0;"><strong>Why this deal?</strong> {deal.get('explanation', 'N/A')}</p>
        </div>

        <div style="display: flex; gap: 2rem; margin: 0.75rem 0; color: #a0a0b0; font-size: 0.85rem;">
            <div>Phone: {phone_html}</div>
            <div>Score: <strong style="color: #667eea;">{score}/100</strong></div>
        </div>

        <div class="score-container">{score_bars}</div>
        <div style="display: flex; gap: 4px; font-size: 0.65rem; color: #707080;">
            <span style="flex:1;">Price</span>
            <span style="flex:1;">Reliability</span>
            <span style="flex:1;">Cost</span>
            <span style="flex:1;">Authenticity</span>
            <span style="flex:1;">Protection</span>
        </div>

        {"<p style='color: #a0a0b0; font-size: 0.85rem; margin-top: 0.75rem;'><em>Negotiation tip:</em> " + deal.get('negotiation_strategy', '') + "</p>" if deal.get('negotiation_strategy') else ""}

        {"<p style='color: #f59e0b; font-size: 0.85rem;'><em>Risk notes:</em> " + deal.get('risk_notes', '') + "</p>" if deal.get('risk_notes') and deal.get('risk_notes') != 'None' else ""}

        <div style="margin-top: 1rem;">
            <a href="{url}" target="_blank" style="
                display: inline-block;
                background: linear-gradient(90deg, #667eea, #764ba2);
                color: white;
                padding: 8px 24px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                font-size: 0.9rem;
            ">View Deal &rarr;</a>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_progress(stage: str):
    """Render search progress indicator."""
    stages = [
        ("Searching the web for deals...", "search"),
        ("Analyzing and comparing prices...", "analyze"),
        ("Ranking and selecting top deals...", "rank"),
    ]

    html = ""
    for label, key in stages:
        if key == stage:
            html += f'<div class="progress-stage active">&#9654; {label}</div>'
        elif stages.index((label, key)) < [s[1] for s in stages].index(stage):
            html += f'<div class="progress-stage done">&#10003; {label}</div>'
        else:
            html += f'<div class="progress-stage">&#9675; {label}</div>'

    st.markdown(html, unsafe_allow_html=True)
