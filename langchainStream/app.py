import streamlit as st
import pandas as pd
from core import NHMQuery, run_structured_query
from agent import create_agent
from io import BytesIO

st.set_page_config("NHM GBIF Explorer", layout="wide")
st.title("NHM GBIF Explorer (LangChain)")

st.sidebar.header("Structured Query")

scientific_name = st.sidebar.text_input("Scientific name", "Quercus robur")
country = st.sidebar.text_input("Country (ISO)", "GB")
year = st.sidebar.text_input("Year range", "1800,1950")
limit = st.sidebar.number_input("Limit", 1, 500, 10)

if st.sidebar.button("Run Query"):
    query = NHMQuery(
        scientific_name=scientific_name,
        country=country,
        year=year,
        limit=limit
    )

    result = run_structured_query(query)
    st.session_state.df = result["example_records"]
    st.session_state.summary = result["summary"]
    st.session_state.filters = result["applied_filters"]
    st.session_state.agent = create_agent(st.session_state.df)
    st.session_state.chat = []

if "df" in st.session_state:

    st.subheader("Applied Filters")
    st.json(st.session_state.filters)

    st.subheader("Summary")
    st.json(st.session_state.summary)

    st.subheader("Records Table (Raw GBIF Data)")
    st.dataframe(st.session_state.df)

    st.subheader("Chat with the Data")

    user_msg = st.chat_input("Ask about the table...")

    if user_msg:
        st.session_state.chat.append(("user", user_msg))
        response = st.session_state.agent.run(user_msg)
        st.session_state.chat.append(("assistant", response))

    for role, msg in st.session_state.chat:
        st.chat_message(role).write(msg)

    st.subheader("Download Raw Data")

    buffer = BytesIO()
    st.session_state.df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    st.download_button(
        label="Download raw GBIF data (Excel)",
        data=buffer,
        file_name="nhm_gbif_raw_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
