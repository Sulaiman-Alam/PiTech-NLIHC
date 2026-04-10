import pandas as pd
import os

CSV_FILE = "housing_programs.csv"

COLUMNS = [
    "program_name",
    "agency",
    "location",
    "target_population",
    "eligibility",
    "benefits",
    "funding_type",
    "summary",
    "source_url"
]

# ----------------------
# SAFE INIT
# ----------------------
def init_csv():
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_FILE, index=False)


# ----------------------
# SAFE SAVE
# ----------------------
def save_to_csv(data):
    init_csv()

    df = pd.read_csv(CSV_FILE)

    row = {
        "program_name": data.get("program_name"),
        "agency": data.get("agency"),
        "location": data.get("location"),
        "target_population": data.get("target_population"),
        "eligibility": data.get("eligibility"),
        "benefits": data.get("benefits"),
        "funding_type": data.get("funding_type"),
        "summary": data.get("summary"),
        "source_url": data.get("source_url", "")
    }

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    df.to_csv(CSV_FILE, index=False)

    return row


# ----------------------
# SAFE LOAD (IMPORTANT FOR STREAMLIT)
# ----------------------
def load_csv():
    init_csv()

    try:
        df = pd.read_csv(CSV_FILE)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=COLUMNS)

    return df
