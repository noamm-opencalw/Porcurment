"""Web search tool — uses crewai_tools.SerperDevTool when available,
falls back to a direct Serper API call otherwise.

Best practice: delegate to the official crewai tool so you get automatic
pagination, caching, and LLM-friendly formatting for free.
"""

import json
import os
from typing import Type

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from src.config.settings import SERPER_API_KEY

# ---------- Try to import the official tool ----------
_SERPER_DEV_TOOL = None
try:
    from crewai_tools import SerperDevTool  # type: ignore[import-untyped]
    _SERPER_DEV_TOOL = SerperDevTool
except ImportError:
    pass


# ---------- Thin wrapper that the agents reference ----------

class WebSearchInput(BaseModel):
    query: str = Field(description="Search query for finding product deals")


def _build_serper_tool():
    """Return a ready-to-use SerperDevTool if possible."""
    if _SERPER_DEV_TOOL is None:
        return None
    api_key = SERPER_API_KEY or os.getenv("SERPER_API_KEY", "")
    if not api_key:
        return None
    return _SERPER_DEV_TOOL(
        api_key=api_key,
        n_results=15,
        country="il",
        locale="he",
    )


class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = (
        "Search the web for product deals, prices, and supplier information. "
        "Returns a list of search results with titles, URLs, and descriptions."
    )
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(self, query: str) -> str:
        # --- Strategy 1: official SerperDevTool ---
        delegate = _build_serper_tool()
        if delegate is not None:
            try:
                return delegate.run(search_query=query)
            except Exception:
                pass  # fall through to manual call

        # --- Strategy 2: direct Serper API call ---
        if SERPER_API_KEY:
            return self._serper_search(query)

        return json.dumps({
            "success": False,
            "error": "No search API key configured. Set SERPER_API_KEY in .env",
        })

    # ----- Direct Serper fallback -----
    @staticmethod
    def _serper_search(query: str) -> str:
        try:
            resp = requests.post(
                "https://google.serper.dev/search",
                headers={
                    "X-API-KEY": SERPER_API_KEY,
                    "Content-Type": "application/json",
                },
                json={"q": query, "num": 15, "gl": "il", "hl": "he"},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            results = [
                {
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "description": item.get("snippet", ""),
                    "source": "serper",
                }
                for item in data.get("organic", [])
            ]
            return json.dumps({
                "success": True,
                "query": query,
                "results_count": len(results),
                "results": results,
            })
        except Exception as e:
            return json.dumps({"success": False, "error": f"Serper search failed: {e}"})
