import streamlit as st
import pandas as pd
from pipeline import run_pipeline
from storage import load_csv

st.title("🏠 Autonomous Rental Housing AI System (Ollama Agents)")

topic = st.text_input("Enter a topic (e.g. NYC rental assistance, Section 8 programs)")

if st.button("Run AI Agents"):
    with st.spinner("Agents are discovering + scraping + extracting..."):
        results = run_pipeline(topic)

    st.success("Done!")

    st.json(results)

# Load dataset
try:
    df = load_csv()
    df = pd.read_csv("housing_programs.csv")
    #st.subheader("Dataset")
    #st.dataframe(df)
except:
    st.info("No data yet.")