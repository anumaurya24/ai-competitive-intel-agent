from dotenv import load_dotenv

from briefing import build_briefing, format_full_briefing, save_briefing
from llm import write_executive_summary

load_dotenv()


def main():
    company = "Anthropic"

    print(f"Building competitive intelligence briefing for: {company}")
    briefing_body = build_briefing(company)

    print("Writing executive summary...")
    exec_summary = write_executive_summary(company, briefing_body)

    full_briefing = format_full_briefing(company, briefing_body, exec_summary)
    output_path = save_briefing(company, full_briefing)

    print(f"\nDone! Briefing saved to: {output_path}")


if __name__ == "__main__":
    main()
