import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

BASE = "https://www.tdhca.texas.gov/"

def fetch(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.text


def clean(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    return soup.get_text(" ")


# -----------------------------
# FIELD EXTRACTORS
# -----------------------------

def extract_htf_name(text):
    match = re.search(r'([A-Z][A-Za-z ]+ Housing Trust Fund)', text)
    return match.group(1) if match else "Texas Housing Trust Fund"


def extract_state():
    return "TX"


def extract_jurisdiction():
    return "statewide"


def extract_agency():
    return "Texas Department of Housing and Community Affairs"


def extract_year(text):
    match = re.search(r'(19|20)\d{2}', text)
    return match.group(0) if match else None


def extract_revenue_sources(text):
    keywords = ["tax", "appropriation", "general fund", "revenue", "bond", "allocation"]
    sentences = re.split(r'(?<=[.!?])\s+', text)

    return [
        s.strip()
        for s in sentences
        if any(k in s.lower() for k in keywords)
    ][:5]


def extract_dedicated_revenue(text):
    # Heuristic: look for explicit "dedicated" statements
    match = re.search(r'(dedicated[^.]{0,120}\.)', text, re.IGNORECASE)
    return match.group(1).strip() if match else None


# -----------------------------
# MAIN PAGE PROCESSOR
# -----------------------------

def process_page(url):
    html = fetch(url)
    text = clean(html)

    return {
        "htf_type": "State",
        "state": extract_state(),
        "local_jurisdiction": extract_jurisdiction(),
        "htf_name": extract_htf_name(text),
        "admin_agency": extract_agency(),
        "date_established": extract_year(text),
        "revenue_sources": extract_revenue_sources(text),
        "dedicated_revenue_source": extract_dedicated_revenue(text),
        "website": url
    }


# -----------------------------
# LINK DISCOVERY
# -----------------------------

def get_links(url):
    html = fetch(url)
    soup = BeautifulSoup(html, "html.parser")

    links = set()
    for a in soup.find_all("a", href=True):
        full = urljoin(url, a["href"])
        if "htf" in full.lower() or "housing" in full.lower():
            links.add(full)

    return list(links)


# -----------------------------
# RUN PIPELINE
# -----------------------------

def run():
    seed = BASE
    urls = get_links(seed)

    print(f"Found {len(urls)} URLs")

    results = []

    for url in urls:
        try:
            print(f"Processing: {url}")
            row = process_page(url)
            results.append(row)
            print(row)

        except Exception as e:
            print(f"Error on {url}: {e}")

    return results


if __name__ == "__main__":
    run()