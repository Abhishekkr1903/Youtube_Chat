# `langchain_google_genai` is an external dependency; provide a helpful message if missing
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError as e:
    raise ImportError(
        "The package 'langchain_google_genai' is required by llm/model.py but is not installed.\n"
        "Please install it (e.g. `pip install langchain-google-genai`).\n"
        f"Original error: {e}"
    )

from dotenv import load_dotenv
import streamlit as st
import os

# Explicitly load .env from project root
load_dotenv(dotenv_path=".env")

def get_llm():
    api_key = st.secrets["GOOGLE_API_KEY"]
    #api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("API key not loaded. Check your .env file.")

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.3,
        google_api_key=api_key
    )
