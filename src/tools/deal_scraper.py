"""Deal scraper tool — uses crewai_tools.ScrapeWebsiteTool when available,
falls back to requests + BeautifulSoup otherwise.

Best practice: let the official ScrapeWebsiteTool handle fetching and
text extraction — it already handles JS rendering, rate-limiting, and
LLM-friendly output.  The agent's prompt tells it *what* to extract
(price, phone, seller), so we don't need custom parsing heuristics
when the official tool is present.
"""

import json
import re
from typing import Type

import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# ---------- Try to import the official tool ----------
_SCRAPE_TOOL = None
try:
    from crewai_tools import ScrapeWebsiteTool  # type: ignore[import-untyped]
    _SCRAPE_TOOL = ScrapeWebsiteTool
except ImportError:
    pass


class DealScraperInput(BaseModel):
    url: str = Field(description="URL of the product listing page to scrape")


class DealScraperTool(BaseTool):
    name: str = "deal_scraper"
    description: str = (
        "Scrape a product listing page to extract deal details: "
        "price, description, seller info, phone number, shipping, and availability. "
        "Pass a URL and get back the page content for analysis."
    )
    args_schema: Type[BaseModel] = DealScraperInput

    def _run(self, url: str) -> str:
        # --- Reject search engine URLs ---
        if "google.com/search" in url or "google.co.il/search" in url or "/search?q=" in url or "bing.com/search" in url:
            return json.dumps({"success": False, "error": "Rejected: search engine URL, not a product page", "url": url})

        # --- Strategy 1: official ScrapeWebsiteTool ---
        if _SCRAPE_TOOL is not None:
            try:
                scraper = _SCRAPE_TOOL(website_url=url)
                return scraper.run()
            except Exception:
                pass  # fall through to manual scraping

        # --- Strategy 2: requests + BeautifulSoup fallback ---
        return self._manual_scrape(url)

    @staticmethod
    def _manual_scrape(url: str) -> str:
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove noise
            for tag in soup(["script", "style", "nav", "footer", "header", "iframe"]):
                tag.decompose()

            # Extract structured metadata
            title = ""
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                title = og_title["content"].strip()
            elif soup.find("title"):
                title = soup.find("title").get_text(strip=True)
            elif soup.find("h1"):
                title = soup.find("h1").get_text(strip=True)

            description = ""
            og_desc = soup.find("meta", property="og:description")
            if og_desc and og_desc.get("content"):
                description = og_desc["content"].strip()[:500]

            seller = ""
            og_site = soup.find("meta", property="og:site_name")
            if og_site and og_site.get("content"):
                seller = og_site["content"].strip()

            # Get clean page text (let the agent parse details)
            body_text = soup.get_text(separator="\n", strip=True)
            # Collapse blank lines
            body_text = re.sub(r"\n{3,}", "\n\n", body_text)
            # Truncate to keep token-friendly
            body_text = body_text[:3000]

            result = {
                "success": True,
                "url": url,
                "title": title,
                "description": description,
                "seller": seller,
                "page_text": body_text,
            }
            return json.dumps(result)

        except Exception as e:
            return json.dumps({"success": False, "url": url, "error": str(e)})
