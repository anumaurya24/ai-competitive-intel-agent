"""
search.py
=========
Everything related to searching the web for company information.
If you ever swap Tavily for a different search tool, this is the ONLY
file you'd need to change.
"""

import os


def search_category(company: str, category_query: str) -> str:
    """
    STEP: Search the web for one category of information about a company.

    'category_query' is a search phrase like "Anthropic funding 2026" —
    this is the same kind of query you typed manually into a browser
    during your manual baseline research.

    Returns raw search result text (unprocessed) for this category.
    """
    from tavily import TavilyClient

    client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    response = client.search(query=category_query, max_results=5)

    combined = ""
    for result in response.get("results", []):
        combined += f"- {result['title']}: {result['content']}\n  (source: {result['url']})\n\n"
    return combined
