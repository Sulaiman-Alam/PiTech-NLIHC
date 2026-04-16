import requests
import pandas as pd

# ==========================
# CONFIG
# ==========================

API_KEY = "aa506fd9cd8b7234dc9e9a31ee4724a9"  # Add your LegiScan API key
BILL_ID = 1898046

if not API_KEY:
    print("Error: LEGI_API_KEY not set.")
    exit()

# ==========================
# STEP 1: Fetch Bill
# ==========================

print("Fetching bill data...")

bill_url = f"https://api.legiscan.com/?key={API_KEY}&op=getBill&id={BILL_ID}"
response = requests.get(bill_url)
data = response.json()

if data.get("status") != "OK":
    print("Error fetching bill:", data)
    exit()

bill = data["bill"]

# ==========================
# STEP 2: Extract Fields
# ==========================

state = bill.get("state")
number = bill.get("bill_number")
description = bill.get("description")
status = bill.get("status_desc")
link = bill.get("state_link")
year = bill.get("session", {}).get("year_start")

# Some fields may not exist directly and may require interpretation
jurisdiction = "State Legislature"
implementing_authority = "New York State Government"
category = "TBD"  # fill manually or categorize later

bill_record = {
    "state/territory": state,
    "jurisdiction": jurisdiction,
    "implementing authority": implementing_authority,
    "number": number,
    "year passed": year,
    "status": status,
    "description": description,
    "link": link,
    "category": category
}

print (bill_record)