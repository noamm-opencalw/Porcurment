from crewai import Agent, Task


def create_broad_search_task(agent: Agent, product_query: str) -> Task:
    return Task(
        description=f"""Search for deals on the specified product: {product_query}

1. Run 3-4 different search queries using variations:
   - "{product_query} best price"
   - "{product_query} wholesale deal"
   - "{product_query} discount coupon"
   - "{product_query} buy online"
2. For each promising result, use the deal_scraper to extract:
   product title, price, URL, seller name, phone number, and description.
3. Search across multiple channels: Amazon, eBay, Walmart, AliExpress,
   manufacturer sites, B2B platforms (Alibaba, ThomasNet), and deal
   aggregators (Slickdeals).
4. Collect at least 10 distinct deals with verified prices.
5. Include deals from both retail and wholesale/B2B channels.
6. For each deal, note the source type: retail, wholesale, marketplace, or b2b.

CRITICAL: Only include deals that are currently available. Skip expired deals.""",
        expected_output="""A JSON list of 10+ deals. Each deal must have:
- title: product name/listing title
- price: numeric price (e.g. 29.99)
- currency: "USD" or original currency
- url: direct link to the deal
- seller: retailer/supplier name
- phone: contact phone number (or "N/A")
- description: 2-3 sentence product description
- source_type: "retail" | "wholesale" | "marketplace" | "b2b"
- shipping_info: shipping cost, "free", or "unknown"

Output ONLY the JSON array, no other text.""",
        agent=agent,
    )


def create_deal_enrichment_task(agent: Agent) -> Task:
    return Task(
        description="""For each of the 10 deals found in the previous search:

1. Visit the deal URL using deal_scraper and extract additional details if missing.
2. Verify the price is current (not expired or out of stock).
3. Look for phone numbers on the seller's contact page if missing.
4. Check for bulk/quantity discount tiers.
5. Note any coupon codes or active promotions.
6. Flag any deals that look suspicious (too cheap, unknown seller, no contact info).

CRITICAL: Keep all deals even if some details are missing — mark them as unverified.""",
        expected_output="""Updated JSON list with enriched deal data. Each deal now includes:
- All fields from the broad search
- verified: true/false (is the price confirmed current?)
- bulk_pricing: discount tiers if available (or null)
- coupon_codes: any active codes (or null)
- suspicious_flags: list of concerns (or empty list [])

Output ONLY the JSON array, no other text.""",
        agent=agent,
    )


def create_deal_analysis_task(agent: Agent, product_query: str) -> Task:
    return Task(
        description=f"""Analyze and score all discovered deals for "{product_query}":

1. Use the price_comparator tool to compare all deal prices and find the market average.
2. Score each deal on 5 criteria (1-10 each):
   - Price competitiveness (vs average market price from comparator)
   - Supplier reliability (known brand? established seller? contact info available?)
   - Total cost (including shipping, handling, taxes if known)
   - Product authenticity (genuine product? authorized reseller? suspicious flags?)
   - Buyer protection (return policy, warranty, payment security)
3. Calculate a weighted total score:
   Price: 30%, Reliability: 25%, Total Cost: 20%, Authenticity: 15%, Protection: 10%
4. Rank all deals by total score (highest first).
5. Select the top 3 deals.
6. For each top deal, write a 2-3 sentence explanation of WHY it's a good deal.
7. Include a negotiation tip for each deal.

CRITICAL: Factor in suspicious_flags when scoring. Deals with many red flags should score low.""",
        expected_output="""JSON object with:
- "all_deals_scored": list of all deals with their scores
- "top_3": list of the 3 best deals, each containing:
  - title, price, url, seller, phone, description
  - total_score (0-100)
  - score_breakdown: {"price": X, "reliability": X, "total_cost": X, "authenticity": X, "protection": X}
  - explanation: why this deal stands out (2-3 sentences)
  - negotiation_tip: how to potentially get a better price

Output ONLY valid JSON, no other text.""",
        agent=agent,
    )


def create_final_recommendation_task(agent: Agent, product_query: str) -> Task:
    return Task(
        description=f"""Review the analyst's top 3 deals for "{product_query}" and produce the final recommendation:

1. Validate each deal meets procurement standards:
   - Has a working URL
   - Has a verifiable price
   - Seller is identifiable
2. Assign a verdict to each deal: BUY / NEGOTIATE / PASS
   - BUY: Great deal, purchase immediately
   - NEGOTIATE: Good potential, try to get a better price first
   - PASS: Not recommended despite being in top 3
3. Add a risk assessment for each deal (low/medium/high + notes).
4. Write a 2-3 sentence executive summary of the overall search results.
5. Ensure ALL required fields are present for UI display:
   description, link, phone, price, and explanation.

CRITICAL: The output must be valid JSON matching the exact schema below.""",
        expected_output="""JSON object:
{{
  "product_searched": "<the product query>",
  "recommendation_summary": "<2-3 sentence executive summary>",
  "deals": [
    {{
      "rank": 1,
      "title": "<product title>",
      "description": "<full description>",
      "price": "<formatted price e.g. $29.99>",
      "price_numeric": 29.99,
      "url": "<link to deal>",
      "phone": "<seller phone or N/A>",
      "seller": "<seller name>",
      "verdict": "BUY",
      "explanation": "<why this is a good deal, 2-3 sentences>",
      "risk_level": "low",
      "risk_notes": "<specific concerns or 'None'>",
      "negotiation_strategy": "<suggested approach>",
      "score_breakdown": {{"price": 9, "reliability": 8, "total_cost": 8, "authenticity": 9, "protection": 7}},
      "total_score": 85
    }}
  ]
}}

Output ONLY valid JSON, no other text.""",
        agent=agent,
    )


def create_send_report_task(
    agent: Agent, product_query: str, recipient_email: str
) -> Task:
    return Task(
        description=f"""Send the top 3 deal recommendations for "{product_query}" via email:

1. Format the deals into a professional HTML email with:
   - Subject: "Procurement Report: Top Deals for {product_query}"
   - A brief intro paragraph
   - A card-style layout for each deal showing: title, price, seller, link, phone
   - Each deal's explanation and verdict
   - A footer with "Generated by Porcurment AI"
2. Send to: {recipient_email}""",
        expected_output="Confirmation JSON with success status and message ID.",
        agent=agent,
    )


def create_search_emails_task(agent: Agent, product_query: str) -> Task:
    return Task(
        description=f"""Check email inbox for supplier quotes related to "{product_query}":

1. Search for recent emails with the product name in the subject line.
2. Extract pricing, terms, and contact info from each email found.
3. Return structured data for each quote.""",
        expected_output="""JSON list of supplier quotes from email:
[{{"from": "...", "subject": "...", "price": "...", "terms": "...", "contact": "..."}}]""",
        agent=agent,
    )
