# AI Competitive Intelligence Agent

An AI agent that automates competitive intelligence research — the manual
work of tracking a company's product launches, funding, partnerships, and
leadership moves across scattered news sources — and turns it into a
structured business briefing with sources and an executive summary.

## The Business Problem

Product and strategy teams spend hours every month manually researching
competitors: checking news sites, press releases, and company blogs for
recent hires, product launches, funding rounds, and leadership changes.
This information is public but scattered, making consistent tracking slow
and easy to fall behind on. Enterprise tools that solve this (e.g., Klue,
Crayon) are priced at $20K-$40K/year, confirming this is a real, valued
business need -- not a hypothetical problem.

## What It Does

Given a company name, the agent:
1. Searches the web across 4 categories: product launches, funding &
   financials, partnerships, and leadership statements
2. Extracts only concrete, dated, sourced facts from raw search results --
   explicitly instructed not to invent information
3. Writes a business-style executive summary (top takeaway, why it matters,
   what to watch next)
4. Outputs everything as a clean, structured Markdown report

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python |
| Web search | Tavily API |
| LLM | Groq (openai/gpt-oss-120b) |
| Config | python-dotenv |
| Output | Markdown |

## Architecture

```
main.py       -> entry point, orchestrates the full pipeline
search.py     -> handles all web search logic (Tavily)
llm.py        -> handles all AI summarization logic (Groq), incl. retry handling
briefing.py   -> builds the category loop and formats the final report
```

Each file has a single responsibility -- swapping the search provider or LLM
provider only requires changing one file, not the whole codebase.

## Sample Output

See [`sample_briefing_anthropic.md`](./sample_briefing_anthropic.md) for a
full example run.

## Evaluation & Known Limitations

I tested this agent against my own manual research on the same company and
found it retrieved comparable major events with proper sourcing. However,
testing also surfaced a genuine, reproducible limitation:

**Date misattribution:** In one run, the agent listed Anthropic CEO Dario
Amodei's essay "We Must Pace the Frontier" as published in February 2026.
The essay was actually published September 12, 2026. Investigating the
source material showed the article referenced a *separate* February 2026
podcast appearance by Amodei -- the model appears to have conflated that
background reference with the article's actual publication date. This
happened consistently across repeated runs, suggesting the model can blend
a secondary detail inside a source with the source's primary subject.

**Other limitations:**
- Search results depend on what's publicly indexed; paywalled or private
  information won't be found
- No independent verification of AI-generated citations beyond the source
  URL being present
- Uses a fixed set of 4 search categories rather than adaptively deciding
  what to search next based on findings (a planned upgrade -- see below)

## What I'd Build Next

- Replace the fixed category loop with a true agentic loop (LangGraph) that
  decides its own next search step based on what it's already found
- Add automated citation verification (does the source URL actually support
  the claim?)
- Add a simple web interface and deploy publicly
- Track briefings over time to highlight what's changed since the last run

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file with:
```
TAVILY_API_KEY=your-key-here
GROQ_API_KEY=your-key-here
```

Run:
```bash
python main.py
```
