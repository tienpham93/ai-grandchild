import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Determine backend URL dynamically (Docker network name or local fallback)
BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:8000")

st.set_page_config(
    page_title="AI Grandchild - Control Center",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ AI Grandchild Control Center Portal")
st.markdown(
    "Welcome to the administrative portal for **AI Grandchild**. This decentralized dashboard "
    "coordinates whitelist databases, manages active families, and monitors active chat operations."
)

st.write("---")

st.header("🔌 System Connections Status")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Backend Server")
    try:
        res = requests.get(f"{BACKEND_URL}/", timeout=2)
        if res.status_code == 200:
            st.success("CONNECTED")
            st.json(res.json())
        else:
            st.warning(f"UNEXPECTED RESPONSE (Status {res.status_code})")
    except Exception:
        st.error("OFFLINE")
        st.caption(f"Could not connect to `{BACKEND_URL}`. Ensure your backend is running.")

with col2:
    st.subheader("Telegram Gateway")
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if token:
        st.success("CONFIGURED")
        st.caption(f"Linked Token: `...{token[-8:]}`")
    else:
        st.error("MISSING")
        st.caption("Please add 'TELEGRAM_BOT_TOKEN' to your .env file.")

with col3:
    st.subheader("Gemini Client Engine")
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        st.success("CONFIGURED")
        st.caption("Gemini Client initialized successfully.")
    else:
        st.error("MISSING")
        st.caption("Please add 'GEMINI_API_KEY' to your .env file.")

st.write("---")

st.subheader("👉 Getting Started")
st.markdown(
    "Use the **Sidebar Navigation** on the left to navigate between different administration pages:\n\n"
    "1. **Account Management:** Organize family directories, manage whitelisted chat sessions, "
    "assign helper roles, and link bank accounts."
)