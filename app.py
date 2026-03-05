import streamlit as st
import requests
import pandas as pd

# ==========================
# CONFIG
# ==========================

API_KEY = "aa506fd9cd8b7234dc9e9a31ee4724a9"

st.title("State Bill Keyword Search")

st.write("Search active legislative bills by state and keyword.")

# User inputs
state = st.text_input("Enter state abbreviation (TX, CA, NY, etc.)").upper()
keyword_input = st.text_input("Enter keywords (comma separated)")

search_button = st.button("Search Bills")

if search_button:

    if not state:
        st.error("Please enter a state abbreviation.")
        st.stop()

    keywords = [k.strip().lower() for k in keyword_input.split(",") if k.strip()]

    # ==========================
    # STEP 1: Get Active Session
    # ==========================

    with st.spinner("Fetching session list..."):

        session_url = f"https://api.legiscan.com/?key={API_KEY}&op=getSessionList&state={state}"
        session_response = requests.get(session_url)
        session_data = session_response.json()

        if session_data.get("status") != "OK":
            st.error("Error fetching session list.")
            st.write(session_data)
            st.stop()

        active_session_id = None

        for session in session_data["sessions"]:
            if session["sine_die"] == 0 and session["special"] == 0:
                active_session_id = session["session_id"]
                st.success(f"Active session found: {session['session_name']}")
                break

        if not active_session_id:
            st.error("No active regular session found.")
            st.stop()

    # ==========================
    # STEP 2: Get Bills
    # ==========================

    with st.spinner("Fetching bills..."):

        master_url = f"https://api.legiscan.com/?key={API_KEY}&op=getMasterList&id={active_session_id}"
        master_response = requests.get(master_url)
        master_data = master_response.json()

        if master_data.get("status") != "OK":
            st.error("Error fetching bills.")
            st.write(master_data)
            st.stop()

        bills = []

        for key, bill in master_data["masterlist"].items():

            if key == "session":
                continue

            title = str(bill.get("title", "")).lower()
            description = str(bill.get("description", "")).lower()

            searchable_text = title + " " + description

            if not keywords:
                bills.append(bill)
            elif any(keyword in searchable_text for keyword in keywords):
                bills.append(bill)

    st.success(f"{len(bills)} bills found.")

    # ==========================
    # STEP 3: Display Results
    # ==========================

    df = pd.DataFrame(bills)

    st.dataframe(df)

    # Download CSV
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"{state}_filtered_bills.csv",
        mime="text/csv"
    )