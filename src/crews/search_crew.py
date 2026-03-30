from crewai import Crew, Process

from src.agents.definitions import create_deal_hunter
from src.tasks.definitions import create_broad_search_task, create_deal_enrichment_task


def build_search_crew(product_query: str, include_international: bool = False) -> Crew:
    hunter = create_deal_hunter()

    return Crew(
        agents=[hunter],
        tasks=[
            create_broad_search_task(hunter, product_query, include_international),
            create_deal_enrichment_task(hunter),
        ],
        process=Process.sequential,
        verbose=True,
        memory=False,
        planning=False,
    )


def run_search(product_query: str, include_international: bool = False) -> str:
    crew = build_search_crew(product_query, include_international)
    result = crew.kickoff()
    return str(result)
