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

    spec_task = create_product_specification_task(specifier, product_query)

    search_task = create_broad_search_task(
        hunter,
        product_query,
        include_international,
        search_queries=refined_queries,
    )
    # Wire spec_task output as context for search_task
    search_task.context = [spec_task]

    enrich_task = create_deal_enrichment_task(hunter)

    return Crew(
        agents=[specifier, hunter],
        tasks=[spec_task, search_task, enrich_task],
        process=Process.sequential,
        verbose=True,
        memory=False,
        planning=False,
    )


def run_search(product_query: str, include_international: bool = False) -> str:
    crew = build_search_crew(product_query, include_international)
    result = crew.kickoff()
    return str(result)
