import os
import time


def call_llm_with_retry(client, prompt: str, max_attempts: int = 3):
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


def summarize_with_llm(company: str, category_name: str, raw_text: str) -> str:
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
