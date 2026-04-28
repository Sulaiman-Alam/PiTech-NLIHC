import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from urllib.parse import urljoin
import pdfplumber
from io import BytesIO

# -----------------------------
# FETCH FUNCTIONS
# -----------------------------

def fetch(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.text


def fetch_pdf(url):
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return BytesIO(r.content)


def clean(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    return soup.get_text(" ")


# -----------------------------
# PDF EXTRACTION
# -----------------------------

def extract_pdf_text(url):
    try:
        pdf_file = fetch_pdf(url)
        text = ""

        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

        return text
    except:
        return ""


# -----------------------------
# NLP-LITE HELPERS
# -----------------------------

def split_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text)


def find_best_sentence(text, keywords):
    sentences = split_sentences(text)

    scored = []
    for s in sentences:
        score = sum(1 for k in keywords if k in s.lower())
        if score > 0:
            scored.append((score, s.strip()))

    scored.sort(reverse=True)
    return scored[0][1] if scored else ""


# -----------------------------
# FIELD EXTRACTION
# -----------------------------

def extract_fields(text):
    year_match = re.search(r'(19|20)\d{2}', text)

    name_patterns = [
        r'([A-Z][A-Za-z ]+ Housing Trust Fund)',
        r'([A-Z][A-Za-z ]+ HTF)',
        r'(Housing Trust Fund Program)',
    ]

    name = ""
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            name = match.group(1)
            break

    return {
        "htf_name": name,
        "date_established": year_match.group(0) if year_match else "",
        "revenue_sources": find_best_sentence(text, ["tax", "revenue", "fund", "bond"]),
        "purpose": find_best_sentence(text, ["purpose", "goal", "provide"]),
        "affordability": find_best_sentence(text, ["income", "affordable", "low-income"]),
    }


# -----------------------------
# CRAWLER
# -----------------------------

def crawl_site(base_url, max_pages=15):
    visited = set()
    to_visit = [base_url]
    results = []

    keywords = ["housing", "trust", "fund", "program", "finance"]

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)

        if url in visited:
            continue

        visited.add(url)

        try:
            if url.endswith(".pdf"):
                text = extract_pdf_text(url)
            else:
                html = fetch(url)
                text = clean(html)

                soup = BeautifulSoup(html, "html.parser")

                for a in soup.find_all("a", href=True):
                    link = urljoin(base_url, a["href"])

                    if base_url in link and link not in visited:
                        to_visit.append(link)

            if any(k in text.lower() for k in keywords):
                results.append((url, text))

        except:
            continue

    return results


# -----------------------------
# AGGREGATION
# -----------------------------

def aggregate_results(pages):
    combined = {
        "htf_name": "",
        "date_established": "",
        "revenue_sources": "",
        "purpose": "",
        "affordability": ""
    }

    for url, text in pages:
        fields = extract_fields(text)

        for key in combined:
            if not combined[key] and fields[key]:
                combined[key] = fields[key]

    return combined


# -----------------------------
# SESSION STATE
# -----------------------------

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame()

if "prefill" not in st.session_state:
    st.session_state.prefill = {}

if "debug" not in st.session_state:
    st.session_state.debug = []

# -----------------------------
# UI
# -----------------------------

st.title("🏠 HTF Full Web Scraper + Data Tool")

url = st.text_input("Enter Base URL")

# -----------------------------
# SCRAPE BUTTON
# -----------------------------

if st.button("🚀 Run Full Scraper"):
    with st.spinner("Crawling site + PDFs..."):

        pages = crawl_site(url)

        st.session_state.debug = pages

        extracted = aggregate_results(pages)

        st.session_state.prefill.update(extracted)

        st.success(f"Processed {len(pages)} pages")

# -----------------------------
# DEBUG VIEW
# -----------------------------

with st.expander("🔍 Debug: Pages + Text"):
    for p in st.session_state.debug[:5]:
        st.write(f"URL: {p[0]}")
        st.text(p[1][:500])

# -----------------------------
# FORM
# -----------------------------

with st.form("form"):

    st.subheader("Core Info")

    htf_type = st.selectbox("HTF Type", ["State", "Local"])
    state = st.text_input("State")
    jurisdiction = st.text_input("Local Jurisdiction", "statewide")

    htf_name = st.text_input("HTF Name", st.session_state.prefill.get("htf_name", ""))
    agency = st.text_input("Administrative Agency")

    year = st.text_input("Date Established", st.session_state.prefill.get("date_established", ""))
    website = st.text_input("Website", url)

    st.subheader("Financial")

    revenue = st.text_area("Revenue Sources", st.session_state.prefill.get("revenue_sources", ""))
    dedicated = st.selectbox("Dedicated Revenue Source?", ["Yes", "No", "Unknown"])

    st.subheader("Fields of Interest")

    income = st.checkbox("Income Restrictions")
    population = st.checkbox("Target Population")
    amount = st.checkbox("Amount of Funding")
    fund_type = st.checkbox("Type of Funding")
    affordability = st.checkbox("Affordability")
    max_funding = st.checkbox("Maximum Funding")
    purpose = st.checkbox("Purpose")
    duration = st.checkbox("Duration")

    submit = st.form_submit_button("Add Entry")

# -----------------------------
# SAVE DATA
# -----------------------------

if submit:
    row = {
        "HTF Type": htf_type,
        "State": state,
        "Local Jurisdiction": jurisdiction,
        "HTF Name": htf_name,
        "Administrative Agency": agency,
        "Date Established": year,
        "Revenue Sources": revenue,
        "Dedicated Revenue Source": dedicated,
        "Website": website,
        "Income Restrictions": income,
        "Target Population": population,
        "Amount of Funding": amount,
        "Type of Funding": fund_type,
        "Affordability": affordability,
        "Maximum Funding": max_funding,
        "Purpose": purpose,
        "Duration": duration,
    }

    st.session_state.data = pd.concat(
        [st.session_state.data, pd.DataFrame([row])],
        ignore_index=True
    )

    st.success("Added to dataset")

# -----------------------------
# TABLE + DOWNLOAD
# -----------------------------

st.subheader("Dataset")
st.dataframe(st.session_state.data)

if not st.session_state.data.empty:
    csv = st.session_state.data.to_csv(index=False).encode("utf-8")

    st.download_button("Download CSV", csv, "htf_data.csv")