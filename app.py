"""Porcurment — AI-Powered Procurement Deal Finder."""

import json
import threading

import pandas as pd
import streamlit as st

from src.db.models import Deal, SearchQuery, get_session, init_db
from src.flows.main_flow import ProcurementFlow
from src.ui.components import (
    inject_custom_css,
    render_deal_card,
    render_search_header,
    render_summary_card,
)
from src.ui.state import add_to_history, init_session_state, set_results

# --- Page Config ---
st.set_page_config(
    page_title="Porcurment — Deal Finder",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()
init_session_state()


def run_search_flow(product_query: str):
    """Run the procurement flow in a thread-safe way."""
    try:
        flow = ProcurementFlow(product_query)
        result = flow.kickoff()
        raw = str(result)

        # Parse the JSON output
        parsed = None
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            start_idx = raw.find("{")
            end_idx = raw.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                try:
                    parsed = json.loads(raw[start_idx:end_idx])
                except json.JSONDecodeError:
                    pass

        if parsed:
            set_results(parsed)
            add_to_history(product_query, parsed)
        else:
            set_results({"error": "Could not parse results", "raw": raw})
            add_to_history(product_query, None)

    except Exception as e:
        set_results({"error": str(e)})
        add_to_history(product_query, None)


# --- Sidebar ---
with st.sidebar:
    st.markdown("### Porcurment")
    st.markdown("*AI Procurement Deal Finder*")
    st.divider()

    # Search History from DB
    st.markdown("#### Search History")
    try:
        init_db()
        session = get_session()
        past_searches = (
            session.query(SearchQuery)
            .order_by(SearchQuery.started_at.desc())
            .limit(20)
            .all()
        )
        for search in past_searches:
            status_icon = (
                "✅" if search.status == "completed" else "❌" if search.status == "failed" else "⏳"
            )
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(
                    f"{status_icon} {search.product_query}",
                    key=f"hist_{search.id}",
                    use_container_width=True,
                ):
                    st.session_state.selected_history = search.id
            with col2:
                st.caption(f"{search.deals_found}")
        session.close()
    except Exception:
        st.caption("No search history yet.")

    st.divider()
    st.markdown("#### Settings")
    st.caption("API Status:")
    from src.config.settings import BRAVE_API_KEY, OPENROUTER_API_KEY, SMTP_USER

    st.caption(f"OpenRouter: {'✅' if OPENROUTER_API_KEY else '❌'}")
    st.caption(f"Brave Search: {'✅' if BRAVE_API_KEY else '❌'}")
    st.caption(f"Email: {'✅' if SMTP_USER else '❌'}")


# --- Main Content ---
render_search_header()

# Search input
col_input, col_btn = st.columns([4, 1])
with col_input:
    product_query = st.text_input(
        "What product are you looking for?",
        placeholder="e.g. wireless keyboard, office chair, monitor 27 inch...",
        label_visibility="collapsed",
    )
with col_btn:
    search_clicked = st.button("Search Deals", type="primary", use_container_width=True)

# Optional filters
with st.expander("Advanced Options"):
    col_a, col_b = st.columns(2)
    with col_a:
        budget_max = st.number_input("Max Budget ($)", min_value=0, value=0, step=10)
    with col_b:
        quantity = st.number_input("Quantity", min_value=1, value=1, step=1)

# --- Handle Search ---
if search_clicked and product_query:
    st.session_state.search_running = True
    st.session_state.results = None

    with st.status("Searching for the best deals...", expanded=True) as status:
        st.write("🔍 Phase 1: Searching the web for deals...")
        st.write("This may take a few minutes as our AI agents search multiple sources.")

        # Run the flow
        try:
            flow = ProcurementFlow(product_query)
            result = flow.kickoff()
            raw = str(result)

            st.write("📊 Phase 2: Analyzing and ranking deals...")

            # Parse
            parsed = None
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                start_idx = raw.find("{")
                end_idx = raw.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    try:
                        parsed = json.loads(raw[start_idx:end_idx])
                    except json.JSONDecodeError:
                        pass

            if parsed:
                st.session_state.results = parsed
                add_to_history(product_query, parsed)
                status.update(label="Search complete!", state="complete", expanded=False)
            else:
                st.session_state.results = {"error": "Could not parse results", "raw": raw}
                status.update(label="Search completed with parsing issues", state="error")

        except Exception as e:
            st.session_state.results = {"error": str(e)}
            status.update(label=f"Search failed: {str(e)[:50]}", state="error")

    st.session_state.search_running = False

# --- Load Historical Results ---
if st.session_state.selected_history and not st.session_state.results:
    try:
        session = get_session()
        search_id = st.session_state.selected_history
        deals = (
            session.query(Deal)
            .filter(Deal.search_id == search_id)
            .order_by(Deal.rank)
            .all()
        )
        if deals:
            search = session.get(SearchQuery, search_id)
            st.session_state.results = {
                "product_searched": search.product_query if search else "",
                "recommendation_summary": "Historical search results loaded from database.",
                "deals": [
                    {
                        "rank": d.rank or i + 1,
                        "title": d.title,
                        "description": d.description,
                        "price": f"${d.price:,.2f}" if d.price else "N/A",
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
                ],
            }
        session.close()
    except Exception:
        pass

# --- Display Results ---
results = st.session_state.results
if results:
    if "error" in results and not results.get("deals"):
        st.error(f"Search error: {results['error']}")
        if results.get("raw"):
            with st.expander("Raw Output"):
                st.code(results["raw"][:3000])
    else:
        # Summary
        if results.get("recommendation_summary"):
            render_summary_card(results["recommendation_summary"])

        # Top 3 Deal Cards
        deals = results.get("deals", [])
        if deals:
            st.markdown("### Top Deals")
            cols = st.columns(min(len(deals), 3))
            for i, deal in enumerate(deals[:3]):
                with cols[i]:
                    render_deal_card(deal, deal.get("rank", i + 1))

            # Action buttons
            st.divider()
            col_actions = st.columns(4)

            with col_actions[0]:
                if st.button("📧 Email Report"):
                    st.info("Configure email in .env to enable sending reports.")

            with col_actions[1]:
                # CSV Export
                df = pd.DataFrame(deals)
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Export CSV",
                    data=csv,
                    file_name=f"porcurment_deals_{results.get('product_searched', 'search')}.csv",
                    mime="text/csv",
                )

            # All Deals Comparison Table
            if len(deals) > 0:
                st.markdown("### All Deals Comparison")
                table_data = []
                for d in deals:
                    price = d.get("price_numeric") or d.get("price", "N/A")
                    table_data.append(
                        {
                            "Rank": d.get("rank", "-"),
                            "Title": d.get("title", "")[:60],
                            "Price": f"${price:,.2f}" if isinstance(price, (int, float)) else price,
                            "Seller": d.get("seller", ""),
                            "Verdict": d.get("verdict", ""),
                            "Score": d.get("total_score", "-"),
                            "Risk": d.get("risk_level", ""),
                        }
                    )
                st.dataframe(
                    pd.DataFrame(table_data),
                    use_container_width=True,
                    hide_index=True,
                )

elif not st.session_state.search_running:
    # Landing state
    st.markdown(
        """
    <div style="text-align: center; padding: 3rem 0; color: #707080;">
        <p style="font-size: 1.2rem;">Enter a product name above to find the best deals</p>
        <p style="font-size: 0.9rem; margin-top: 1rem;">
            Our AI agents will search the web, compare prices, and recommend the top 3 deals
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
