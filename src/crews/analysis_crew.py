from crewai import Crew, Process

from src.agents.definitions import create_deal_analyst, create_procurement_lead
from src.tasks.definitions import (
    create_deal_analysis_task,
    create_final_recommendation_task,
)


def build_analysis_crew(product_query: str) -> Crew:
    analyst = create_deal_analyst()
    lead = create_procurement_lead()

    return Crew(
        agents=[analyst, lead],
        tasks=[
            create_deal_analysis_task(analyst, product_query),
            create_final_recommendation_task(lead, product_query),
        ],
        process=Process.sequential,
        verbose=True,
        memory=False,
        planning=False,
    )


def run_analysis(product_query: str, search_results: str) -> str:
    crew = build_analysis_crew(product_query)
    result = crew.kickoff(inputs={"search_results": search_results})
    return str(result)
