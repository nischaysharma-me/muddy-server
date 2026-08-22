"""Web search tool simulation and connector."""

from typing import Dict, Any, List
from app.tools.registry import registry


@registry.register(
    name="web_search",
    description="Searches for information on a given topic, query, or technical question.",
    category="research",
)
async def web_search_mock(query: str, max_results: int = 3) -> Dict[str, Any]:
    """Asynchronously performs information lookup for the agent."""
    # Production-ready structure, expandable with DuckDuckGo, Tavily, or Google Search API
    return {
        "query": query,
        "results": [
            {
                "title": f"Overview on {query}",
                "snippet": f"Detailed domain context and factual knowledge related to '{query}'. High performance agentic patterns utilize graph-based workflows.",
                "url": f"https://docs.muddy-server.local/search?q={query}",
            }
        ][:max_results],
        "count": 1,
    }
