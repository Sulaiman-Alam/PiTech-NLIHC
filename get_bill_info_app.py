import streamlit as st
import requests
import pandas as pd

API_KEY = "YOUR_API_KEY"

st.title("State Bill Keyword Search")

state = st.text_input("Enter state abbreviation (TX, CA, NY)").upper()
keywords_input = st.text_input("Enter keywords (comma separated)")

search_button = st.button("Search Bills")

if search_button:

    keywords = [k.strip().lower() for k in keywords_input.split(",") if k.strip()]

    # Get session list
    session_url = f"https://api.legiscan.com/?key={API_KEY}&op=getSessionList&state={state}"
    session_data = requests.get(session_url).json()

    active_session_id = None

    for session in session_data["sessions"]:
        if session["sine_die"] == 0 and session["special"] == 0:
            active_session_id = session["session_id"]
            st.success(f"Active session: {session['session_name']}")
            break

    if not active_session_id:
        st.error("No active session found.")
        st.stop()

    # Get bills
    master_url = f"https://api.legiscan.com/?key={API_KEY}&op=getMasterList&id={active_session_id}"
    master_data = requests.get(master_url).json()

    bills = []

    for key, bill in master_data["masterlist"].items():

        if key == "session":
            continue

        title = str(bill.get("title", "")).lower()
        description = str(bill.get("description", "")).lower()

        searchable_text = title + " " + description

        if not keywords or any(k in searchable_text for k in keywords):
            bills.append(bill)

    st.write(f"### {len(bills)} Bills Found")

    # Display bills with button
    for bill in bills:

        col1, col2 = st.columns([4,1])

        with col1:
            st.write(f"**{bill['bill_number']}**: {bill['title']}")

        with col2:
            if st.button("Get Information", key=bill["bill_id"]):

                bill_url = f"https://api.legiscan.com/?key={API_KEY}&op=getBill&id={bill['bill_id']}"
                bill_data = requests.get(bill_url).json()

                bill_info = bill_data["bill"]

                df = pd.json_normalize(bill_info)

                csv = df.to_csv(index=False).encode("utf-8")

                st.download_button(
                    label="Download Bill CSV",
                    data=csv,
                    file_name=f"{bill['bill_number']}_info.csv",
                    mime="text/csv"
                )