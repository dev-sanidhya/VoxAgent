import streamlit as st


def run_app() -> None:
    st.set_page_config(page_title="VoxAgent", page_icon="🎙️", layout="wide")
    st.title("VoxAgent")
    st.info("Project skeleton initialized. Core agent pipeline will be wired next.")
