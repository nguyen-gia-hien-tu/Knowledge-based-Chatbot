import time

import streamlit as st
from utils.utils import setup_tools

st.set_page_config(
    page_title="Knowledge-based Chatbot",
    page_icon="🤖",
)

st.title("Welcome to the Knowledge-based Chatbot! 👋")

st.sidebar.success("Select if you want to chat with the bot or upload documents")

st.markdown(
    """
    This is a knowledge-based chatbot where you can upload your own documents
    and chat with the AI assistant. The AI assistant will answer your questions
    based on the uploaded documents.
    - To chat with the AI assistant, select the "🤖 Chatbot" option from the sidebar
    - To upload documents, select the "📂 Upload Documents" option from the sidebar
"""
)

setup_tools()
