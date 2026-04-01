import json

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

    # If the caller already has refined queries, use them; otherwise the
    # specifier task output will be parsed and injected at runtime.
    # We use a callback on spec_task to extract search_queries and pass them
    # to the broad search task via a shared context approach.
    # For simplicity and compatibility with CrewAI sequential process,
    # we pass refined_queries if provided; otherwise the spec task output
    # is available as context for the broad search task.
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
