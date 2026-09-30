import os


def search_category(company: str, category_query: str) -> str:
    from tavily import TavilyClient

    client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    response = client.search(query=category_query, max_results=5)

    combined = ""
    for result in response.get("results", []):
        combined += f"- {result['title']}: {result['content']}\n  (source: {result['url']})\n\n"
    return combined
