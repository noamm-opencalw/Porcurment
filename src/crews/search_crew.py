from crewai import Crew, Process

from src.agents.definitions import create_deal_hunter, create_product_specifier
from src.tasks.definitions import (
    create_broad_search_task,
    create_deal_enrichment_task,
    create_product_specification_task,
)


def build_search_crew(
    product_query: str,
    include_international: bool = False,
    refined_queries: list[str] | None = None,
) -> Crew:
    specifier = create_product_specifier()
    hunter = create_deal_hunter()

    tasks = [
        create_product_specification_task(specifier, product_query),
        create_broad_search_task(hunter, product_query, include_international, refined_queries),
        create_deal_enrichment_task(hunter),
    ]

    return Crew(
        agents=[specifier, hunter],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
        memory=False,
        planning=False,
    )


def run_search(product_query: str, include_international: bool = False) -> str:
    crew = build_search_crew(product_query, include_international)
    result = crew.kickoff()
    return str(result)
