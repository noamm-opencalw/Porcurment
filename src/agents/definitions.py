from crewai import Agent, LLM

from src.config.settings import (
    CREWAI_CHEAP_MODEL,
    CREWAI_DEFAULT_MODEL,
    CREWAI_PREMIUM_MODEL,
    OPENROUTER_API_KEY,
)
from src.tools.deal_scraper import DealScraperTool
from src.tools.email_tool import EmailTool
from src.tools.price_comparator import PriceComparatorTool
from src.tools.web_search import WebSearchTool

llm_default = LLM(
    model=CREWAI_DEFAULT_MODEL,
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)
llm_premium = LLM(
    model=CREWAI_PREMIUM_MODEL,
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)
llm_cheap = LLM(
    model=CREWAI_CHEAP_MODEL,
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)


def create_deal_hunter() -> Agent:
    return Agent(
        role="Procurement Deal Hunter",
        goal=(
            "Search the internet exhaustively to find the 10 best deals for a given product. "
            "Use multiple search queries, variations, and sources. Look at major retailers, "
            "wholesale suppliers, marketplace listings, and B2B platforms. Focus on finding "
            "real, currently available deals with verifiable prices."
        ),
        backstory=(
            "You are a veteran procurement specialist with 15 years in supply chain "
            "management for Fortune 500 companies. You know every sourcing trick: "
            "searching by manufacturer part number, checking liquidation sites, "
            "comparing authorized distributors vs gray market, and timing purchases "
            "around seasonal sales. You search systematically — first broad, then "
            "narrow — and you never settle for the first page of results."
        ),
        llm=llm_default,
        tools=[WebSearchTool(), DealScraperTool()],
        memory=False,
        verbose=True,
        max_iter=12,
        allow_delegation=False,
    )


def create_deal_analyst() -> Agent:
    return Agent(
        role="Procurement Analyst & Deal Evaluator",
        goal=(
            "Analyze and rank the discovered deals by value. For each deal, assess: "
            "true total cost (including shipping, taxes, minimum order quantities), "
            "supplier reliability, product authenticity risk, return policy, and "
            "value-for-money ratio. Select the top 3 deals with clear justification."
        ),
        backstory=(
            "You are a senior procurement analyst who has saved companies millions "
            "through rigorous deal evaluation. You know that the cheapest price is "
            "not always the best deal — you factor in supplier reputation, shipping "
            "time, warranty coverage, and hidden costs. You've been burned by too-good-"
            "to-be-true deals from unreliable vendors, so you always verify legitimacy. "
            "Your evaluations are data-driven and include a clear scoring rubric."
        ),
        llm=llm_premium,
        tools=[WebSearchTool(), PriceComparatorTool()],
        memory=False,
        verbose=True,
        max_iter=8,
        allow_delegation=False,
    )


def create_email_agent() -> Agent:
    return Agent(
        role="Procurement Communications Specialist",
        goal=(
            "Handle all email-related procurement tasks: read incoming supplier quotes "
            "and RFP responses, draft inquiry emails to suppliers for bulk pricing, "
            "send deal summary reports to stakeholders. Professional, concise communication."
        ),
        backstory=(
            "You are a procurement coordinator who handles 200+ supplier emails daily. "
            "You know how to write emails that get responses: clear subject lines, "
            "specific quantity requests, and professional but firm tone. You can "
            "extract key data points (price, MOQ, lead time, contact) from messy "
            "supplier emails. You always include a call-to-action and follow-up date."
        ),
        llm=llm_cheap,
        tools=[EmailTool()],
        memory=False,
        verbose=True,
        max_iter=5,
        allow_delegation=False,
    )


def create_procurement_lead() -> Agent:
    return Agent(
        role="Chief Procurement Officer",
        goal=(
            "Oversee the entire deal-finding operation. Review the top 3 deals from "
            "the analyst, validate they meet procurement standards, and produce a "
            "final recommendation report with clear BUY/NEGOTIATE/PASS verdicts. "
            "Ensure all results include: description, link, phone, price, and "
            "a compelling explanation of why each deal is worthwhile."
        ),
        backstory=(
            "You are a CPO who has negotiated $500M+ in contracts across industries. "
            "You think beyond price: total cost of ownership, supplier diversification, "
            "payment terms, and strategic value. You present findings to executives "
            "in a clear, actionable format. Every recommendation includes a risk "
            "assessment and a suggested negotiation strategy."
        ),
        llm=llm_premium,
        tools=[WebSearchTool(), PriceComparatorTool()],
        memory=False,
        verbose=True,
        max_iter=6,
        allow_delegation=True,
    )
