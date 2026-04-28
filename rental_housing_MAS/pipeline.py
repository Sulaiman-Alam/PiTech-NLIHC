from agents import extract_agent, validate_agent
from scraper import scrape_url
from storage import save_to_csv
from discovery import discovery_agent

def run_pipeline(topic):
    print("🔍 Finding websites...")

    urls = discovery_agent(topic)

    results = []

    for url in urls:
        print("🕷️ Scraping:", url)

        text = scrape_url(url)
        if not text:
            print("Skipping URL (no content):", url)
            continue

        print("🤖 Extracting...")
        extracted = extract_agent(text, url)

        print("🧹 Validating...")
        cleaned = validate_agent(extracted)

        save_to_csv(cleaned)
        results.append(cleaned)

    return results

import json
import re

def clean_llm_output(text):
    """
    Extracts JSON even if LLM wraps it in text or ``` blocks
    """

    # remove ```json blocks
    text = re.sub(r"```json", "", text)
    text = text.replace("```", "")

    # try to find first { ... } block
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group())
        except:
            return None

    return None