"""
main.py
=======
AI Competitive Intelligence Agent — Entry Point
================================================
This is the file you actually run: `py main.py`

It ties together the other three files:
- search.py    -> finds raw information on the web
- llm.py       -> turns raw information into clean facts + an exec summary
- briefing.py  -> assembles everything into one Markdown report and saves it

WHAT YOU NEED TO RUN THIS:
- pip install -r requirements.txt
- A Tavily API key (https://tavily.com — free tier)
- A Groq API key (https://console.groq.com/keys — free tier)
- Both saved in a .env file: TAVILY_API_KEY and GROQ_API_KEY
"""

from dotenv import load_dotenv

from briefing import build_briefing, format_full_briefing, save_briefing
from llm import write_executive_summary

load_dotenv()


def main():
    company = "Anthropic"  # <-- change this to test other companies

    print(f"Building competitive intelligence briefing for: {company}")
    briefing_body = build_briefing(company)

    print("Writing executive summary...")
    exec_summary = write_executive_summary(company, briefing_body)

    full_briefing = format_full_briefing(company, briefing_body, exec_summary)
    output_path = save_briefing(company, full_briefing)

    print(f"\nDone! Briefing saved to: {output_path}")


if __name__ == "__main__":
    main()
