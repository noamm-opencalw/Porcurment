import json
from typing import Type

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from src.config.settings import BRAVE_API_KEY, SERPER_API_KEY, MAX_SEARCH_RESULTS


class WebSearchInput(BaseModel):
    query: str = Field(description="Search query for finding product deals")
    search_type: str = Field(
        default="web",
        description="Type of search: 'web', 'news', or 'both'",
    )
    max_results: int = Field(
        default=MAX_SEARCH_RESULTS,
        description="Maximum number of results to return",
    )
    freshness: str = Field(
        default="pm",
        description="Freshness filter: 'pd' (past day), 'pw' (past week), 'pm' (past month)",
    )


class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = (
        "Search the web for product deals, prices, and supplier information. "
        "Uses Brave Search API for comprehensive results. "
        "Returns a list of search results with titles, URLs, and descriptions."
    )
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(
        self,
        query: str,
        search_type: str = "web",
        max_results: int = MAX_SEARCH_RESULTS,
        freshness: str = "pm",
    ) -> str:
        results = []

        if BRAVE_API_KEY:
            results = self._brave_search(query, search_type, max_results, freshness)

        if not results and SERPER_API_KEY:
            results = self._serper_search(query, max_results)

        if not results:
            return json.dumps(
                {
                    "success": False,
                    "error": "No search API keys configured. Set BRAVE_API_KEY or SERPER_API_KEY in .env",
                }
            )

        return json.dumps(
            {
                "success": True,
                "query": query,
                "results_count": len(results),
                "results": results,
            }
        )

    def _brave_search(
        self, query: str, search_type: str, max_results: int, freshness: str
    ) -> list:
        results = []
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": BRAVE_API_KEY,
        }

        if search_type in ("web", "both"):
            try:
                resp = requests.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    headers=headers,
                    params={
                        "q": query,
                        "count": max_results,
                        "freshness": freshness,
                        "country": "IL",
                    },
                    timeout=15,
                )
                resp.raise_for_status()
                data = resp.json()
                for item in data.get("web", {}).get("results", []):
                    results.append(
                        {
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "description": item.get("description", ""),
                            "source": "brave_web",
                        }
                    )
            except Exception as e:
                results.append({"error": f"Brave web search failed: {str(e)}"})

        if search_type in ("news", "both"):
            try:
                resp = requests.get(
                    "https://api.search.brave.com/res/v1/news/search",
                    headers=headers,
                    params={"q": query, "count": min(max_results, 10)},
                    timeout=15,
                )
                resp.raise_for_status()
                data = resp.json()
                for item in data.get("results", []):
                    results.append(
                        {
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "description": item.get("description", ""),
                            "source": "brave_news",
                        }
                    )
            except Exception as e:
                results.append({"error": f"Brave news search failed: {str(e)}"})

        return results

    def _serper_search(self, query: str, max_results: int) -> list:
        results = []
        try:
            resp = requests.post(
                "https://google.serper.dev/search",
                headers={
                    "X-API-KEY": SERPER_API_KEY,
                    "Content-Type": "application/json",
                },
                json={"q": query, "num": max_results, "gl": "il", "hl": "he"},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("organic", []):
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "description": item.get("snippet", ""),
                        "source": "serper",
                    }
                )
        except Exception as e:
            results.append({"error": f"Serper search failed: {str(e)}"})

        return results
