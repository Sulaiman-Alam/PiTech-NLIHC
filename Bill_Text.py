import streamlit as st
import requests
import base64

API_KEY = "aa506fd9cd8b7234dc9e9a31ee4724a9"

st.title("Bill Text Viewer")

st.write("Enter a bill ID to view full bill text.")

bill_id = st.text_input("Enter Bill ID")

# -------------------------
# Helper Functions
# -------------------------

@st.cache_data
def get_bill_details(bill_id):
    url = f"https://api.legiscan.com/?key={API_KEY}&op=getBill&id={bill_id}"
    return requests.get(url).json()["bill"]

@st.cache_data
def get_bill_text(doc_id):
    url = f"https://api.legiscan.com/?key={API_KEY}&op=getBillText&id={doc_id}"
    data = requests.get(url).json()["text"]

    decoded = base64.b64decode(data["doc"]).decode("utf-8", errors="ignore")

    return decoded, data.get("type"), data.get("date")

# -------------------------
# Fetch + Display Text
# -------------------------

if st.button("Get Bill Text"):

    if not bill_id:
        st.error("Please enter a bill ID.")
        st.stop()

    bill_info = get_bill_details(bill_id)

    texts = bill_info.get("texts", [])

    if not texts:
        st.warning("No bill text available.")
        st.stop()

    st.success(f"Bill: {bill_info.get('bill_number')}")

    # Let user choose version
    options = {
        f"{t.get('type')} ({t.get('date')})": t["doc_id"]
        for t in texts
    }

    selected_version = st.selectbox(
        "Select bill version:",
        options=list(options.keys())
    )

    doc_id = options[selected_version]

    text, doc_type, doc_date = get_bill_text(doc_id)

    st.subheader(f"{doc_type} — {doc_date}")

    st.text_area("Bill Text", text, height=500)

    st.download_button(
        label="Download Text File",
        data=text,
        file_name=f"{bill_info.get('bill_number','bill')}.txt",
        mime="text/plain"
    )