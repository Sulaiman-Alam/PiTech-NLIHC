import requests
import pandas as pd
import os
import time

# ==========================
# CONFIG
# ==========================

API_KEY = "aa506fd9cd8b7234dc9e9a31ee4724a9"  # insert your key here

if not API_KEY:
    print("Error: API_KEY not set.")
    exit()

STATES = [
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
    "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
    "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"
]

OUTPUT_DIR = "masterlists"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================
# PROCESS STATES
# ==========================

for STATE in STATES:

    print(f"\n===== Processing {STATE} =====")

    # STEP 1: Get active session
    session_url = f"https://api.legiscan.com/?key={API_KEY}&op=getSessionList&state={STATE}"
    session_response = requests.get(session_url)
    session_data = session_response.json()

    if session_data.get("status") != "OK":
        print(f"Skipping {STATE} (session fetch failed)")
        continue

    active_session_id = None

    for session in session_data["sessions"]:
        if session["sine_die"] == 0 and session["special"] == 0:
            active_session_id = session["session_id"]
            print("Active session:", session["session_name"])
            break

    if not active_session_id:
        print(f"No active session for {STATE}")
        continue

    # STEP 2: Get master list
    master_url = f"https://api.legiscan.com/?key={API_KEY}&op=getMasterList&id={active_session_id}"
    master_response = requests.get(master_url)
    master_data = master_response.json()

    if master_data.get("status") != "OK":
        print(f"Skipping {STATE} (masterlist failed)")
        continue

    records = []

    for key, bill in master_data["masterlist"].items():

        if key == "session":
            continue

        record = {
            "state": STATE,
            "bill_id": bill.get("bill_id"),
            "bill_number": bill.get("bill_number"),
            "title": bill.get("title"),
            "description": bill.get("description"),
            "status": bill.get("status"),
            "status_date": bill.get("status_date"),
            "url": bill.get("url")
        }

        records.append(record)

    print(f"Total bills: {len(records)}")

    # STEP 3: Save CSV
    df = pd.DataFrame(records)
    filepath = os.path.join(OUTPUT_DIR, f"{STATE}_masterlist.csv")
    df.to_csv(filepath, index=False)

    print(f"Saved: {filepath}")

    time.sleep(0.5)  # be nice to API

print("\n✅ Done! All state masterlists saved.")