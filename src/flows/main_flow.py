"""Main procurement flow: search for deals → analyze → recommend top 3."""

import json
import sys
from datetime import datetime, timezone

from crewai.flow.flow import Flow, listen, start

from src.crews.analysis_crew import build_analysis_crew
from src.crews.search_crew import build_search_crew
from src.db.models import Deal, SearchQuery, SearchResult, get_session, init_db


class ProcurementFlow(Flow):
    """Flow: initialize → search → analyze → finalize."""

    def __init__(self, product_query: str):
        super().__init__()
        self.product_query = product_query
        self.state = {
            "product_query": product_query,
            "search_results": "",
            "final_output": "",
        }

    @start()
    def initialize(self):
        """Initialize database and create search record."""
        init_db()
        session = get_session()
        search = SearchQuery(
            product_query=self.product_query,
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        session.add(search)
        session.commit()
        self.state["search_id"] = search.id
        session.close()
        print(f"[Porcurment] Starting search for: {self.product_query}")
        return {"status": "initialized", "search_id": search.id}

    @listen(initialize)
    def run_search(self, init_result):
        """Run the search crew to find 10+ deals."""
        print("[Porcurment] Phase 1: Searching for deals...")
        crew = build_search_crew(self.product_query)
        result = crew.kickoff()
        self.state["search_results"] = str(result)
        print(f"[Porcurment] Search complete. Raw output length: {len(str(result))}")
        return str(result)

    @listen(run_search)
    def run_analysis(self, search_result):
        """Run the analysis crew to rank and recommend top 3."""
        print("[Porcurment] Phase 2: Analyzing and ranking deals...")
        crew = build_analysis_crew(self.product_query)
        result = crew.kickoff(inputs={"search_results": str(search_result)})
        self.state["final_output"] = str(result)
        print("[Porcurment] Analysis complete.")
        return str(result)

    @listen(run_analysis)
    def finalize(self, analysis_result):
        """Save results to database and return final output."""
        print("[Porcurment] Phase 3: Saving results...")
        session = get_session()
        search_id = self.state.get("search_id")

        # Try to parse the final JSON output
        final_data = None
        raw = str(analysis_result)
        try:
            final_data = json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract JSON from the output
            start_idx = raw.find("{")
            end_idx = raw.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                try:
                    final_data = json.loads(raw[start_idx:end_idx])
                except json.JSONDecodeError:
                    pass

        if final_data and search_id:
            # Save deals to DB
            deals = final_data.get("deals", [])
            deal_ids = []
            for deal_data in deals:
                deal = Deal(
                    search_id=search_id,
                    title=deal_data.get("title", ""),
                    description=deal_data.get("description", ""),
                    price=deal_data.get("price_numeric"),
                    url=deal_data.get("url", ""),
                    seller=deal_data.get("seller", ""),
                    phone=deal_data.get("phone", "N/A"),
                    rank=deal_data.get("rank"),
                    total_score=deal_data.get("total_score"),
                    explanation=deal_data.get("explanation", ""),
                    verdict=deal_data.get("verdict", ""),
                    risk_level=deal_data.get("risk_level", ""),
                    risk_notes=deal_data.get("risk_notes", ""),
                    negotiation_strategy=deal_data.get("negotiation_strategy", ""),
                    score_breakdown=deal_data.get("score_breakdown"),
                )
                session.add(deal)
                session.flush()
                deal_ids.append(deal.id)

            # Save search result
            search_result = SearchResult(
                search_id=search_id,
                recommendation_summary=final_data.get("recommendation_summary", ""),
                top_deal_ids=deal_ids,
                raw_output=raw,
            )
            session.add(search_result)

            # Update search query status
            search_query = session.get(SearchQuery, search_id)
            if search_query:
                search_query.status = "completed"
                search_query.deals_found = len(deals)
                search_query.completed_at = datetime.now(timezone.utc)

            session.commit()
            print(f"[Porcurment] Saved {len(deals)} deals to database.")
        else:
            # Mark as failed if we couldn't parse
            if search_id:
                search_query = session.get(SearchQuery, search_id)
                if search_query:
                    search_query.status = "failed"
                    search_query.completed_at = datetime.now(timezone.utc)
                session.commit()
            print("[Porcurment] Warning: Could not parse final output as JSON.")

        session.close()

        self.state["final_output"] = raw
        return raw


def run_flow(product_query: str) -> str:
    """Run the full procurement flow and return the result."""
    flow = ProcurementFlow(product_query)
    result = flow.kickoff()
    return str(result)


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "wireless keyboard"
    print(f"Running Porcurment for: {query}")
    output = run_flow(query)
    print("\n=== FINAL OUTPUT ===")
    print(output)
