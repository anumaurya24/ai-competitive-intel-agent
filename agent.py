"""
AI Competitive Intelligence Agent — Starter Version
=====================================================
This script is intentionally simple. It follows the "observe -> decide ->
act -> repeat" agent pattern, but written step-by-step so you can see and
understand every piece before you swap in a real agent framework
(LangGraph/CrewAI) later, per your project blueprint's Phase 4.

WHAT THIS SCRIPT DOES:
1. Takes a company name (today: "Anthropic")
2. Searches for information in 3 categories: product launches, funding, news
3. Sends the raw search results to an LLM (Claude) to summarize
4. Writes a structured Markdown briefing to a file

WHAT YOU NEED TO RUN THIS YOURSELF (not run in this sandbox — no network here):
- pip install google-generativeai tavily-python python-dotenv (see requirements.txt)
- A Gemini API key — FREE tier, no credit card needed (https://aistudio.google.com/apikey)
- A Tavily API key for web search (https://tavily.com — free tier available)
- Put both in a .env file: GEMINI_API_KEY and TAVILY_API_KEY

WHY TAVILY: it's an LLM-native search API, purpose-built for AI agents,
and it's what real competitive-intelligence agent builds use under the hood
(see your blueprint's tooling notes).
"""

import os
import time
from datetime import date
from dotenv import load_dotenv

load_dotenv()  # reads your .env file and loads OPENAI_API_KEY / TAVILY_API_KEY


def call_llm_with_retry(client, prompt: str, max_attempts: int = 3):
    """
    STEP: A small safety wrapper. Servers occasionally return a temporary
    'high demand' or rate-limit error that isn't really your code's fault.
    Instead of crashing, this tries again a few times with a short pause.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return client.chat.completions.create(
                model="openai/gpt-oss-120b",
                max_tokens=1500,
                reasoning_effort="low",
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as e:
            if "429" in str(e) or "503" in str(e) or "UNAVAILABLE" in str(e):
                if attempt < max_attempts:
                    print(f"  (Server busy, retrying in 10s... attempt {attempt}/{max_attempts})")
                    time.sleep(10)
                    continue
            raise

# These imports will only work once you `pip install` them locally.
# We import them inside functions/try-blocks so this file can still be
# READ and understood even before you've installed anything.


def search_category(company: str, category_query: str) -> str:
    """
    STEP: Search the web for one category of information about a company.

    'category_query' is a search phrase like "Anthropic funding 2026" —
    this is the same kind of query you typed manually into a browser
    during your manual baseline research.

    Returns raw search result text (unprocessed) for this category.
    """
    from tavily import TavilyClient  # local import: only needed here

    client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    response = client.search(query=category_query, max_results=5)

    # Combine the top results into one text blob for the LLM to read
    combined = ""
    for result in response.get("results", []):
        combined += f"- {result['title']}: {result['content']}\n  (source: {result['url']})\n\n"
    return combined


def summarize_with_llm(company: str, category_name: str, raw_text: str) -> str:
    """
    STEP: Send raw search results to Groq (free tier, Llama model) and ask
    it to extract only the genuinely new, concrete facts — with sources.
    This is the "reasoning" step in the agent loop: deciding what's
    actually worth reporting.
    """
    from groq import Groq

    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    prompt = f"""You are a business analyst preparing a competitive intelligence
briefing on {company}. Below are raw search results for the category:
"{category_name}".

Extract only concrete, dated facts (e.g., specific announcements, numbers,
dates). Ignore vague or repeated information. If nothing concrete is found,
say "No significant findings in this category" — do not invent facts.
For every fact, include the source in parentheses.

Raw search results:
{raw_text}

Respond with a short bulleted list only, no preamble."""

    response = call_llm_with_retry(client, prompt)
    return response.choices[0].message.content


def write_executive_summary(company: str, full_briefing_body: str) -> str:
    """
    STEP: The 'business judgment' layer. Instead of just listing facts,
    this asks the AI to step back and think like an analyst: what actually
    matters, and what should a strategy/product team do about it? This is
    what turns a data dump into a business deliverable.
    """
    from groq import Groq

    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    prompt = f"""You are a senior business/product strategist. Below is a raw
competitive intelligence briefing on {company}, organized by category.

{full_briefing_body}

Write a short executive summary with exactly three parts:
1. TOP TAKEAWAY: the single most important thing happening at this company
   right now, in one sentence.
2. WHY IT MATTERS: 2-3 sentences on what this signals about their strategy
   or momentum.
3. WATCH NEXT: one specific thing a competitor or partner should pay
   attention to going forward.

Be specific and concrete — reference actual facts from the briefing above,
not generic statements. Keep the whole thing under 150 words."""

    response = call_llm_with_retry(client, prompt)
    return response.choices[0].message.content


def build_briefing(company: str) -> str:
    """
    STEP: The main loop. For each category, search -> summarize -> collect.
    This is a simplified version of "observe -> decide -> act -> repeat" —
    right now the categories are fixed, but in Phase 4 of your blueprint,
    you'll upgrade this so the agent DECIDES which categories to dig deeper
    into based on what it finds (e.g., if funding news is thin, search again
    with a different phrasing).
    """
    categories = {
        "Product Launches": f"{company} new product launch announcement 2026",
        "Funding & Financials": f"{company} funding round valuation 2026",
        "Partnerships & Notable Moves": f"{company} partnership announcement 2026",
        "Leadership & Public Statements": f"{company} executive statement leadership 2026",
    }

    briefing_sections = []
    for category_name, query in categories.items():
        print(f"Searching: {category_name}...")
        raw_results = search_category(company, query)
        summary = summarize_with_llm(company, category_name, raw_results)
        briefing_sections.append(f"## {category_name}\n{summary}\n")
        time.sleep(13)  # stay under the free tier's 5-requests-per-minute limit

    return "\n".join(briefing_sections)


def main():
    company = "Anthropic"  # <-- change this to test other companies later

    print(f"Building competitive intelligence briefing for: {company}")
    briefing_body = build_briefing(company)

    print("Writing executive summary...")
    exec_summary = write_executive_summary(company, briefing_body)

    today = date.today().isoformat()
    full_briefing = f"""# Competitive Intelligence Briefing: {company}
### Generated: {today}

## Executive Summary
{exec_summary}

---

{briefing_body}

---
*This briefing was generated by an AI agent. Verify facts against sources
before using in a business decision.*
"""

    output_path = f"briefing_{company.lower()}_{today}.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_briefing)

    print(f"\nDone! Briefing saved to: {output_path}")


if __name__ == "__main__":
    main()