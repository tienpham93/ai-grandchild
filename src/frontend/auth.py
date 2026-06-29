import os
import requests
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:8000")

def check_auth() -> bool:
    """
    Checks session authentication status. 
    Renders login screen and stops page rendering if unauthorized.
    """
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        # User is authenticated, render a logout button at the bottom of the sidebar
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Log Out", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        return True

    # --- RENDER LOGIN INTERFACE ---
    # Hide sidebar navigation pages by injecting custom CSS
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none !important;}
        </style>
    """, unsafe_allow_html=True)

    col_space1, col_form, col_space2 = st.columns([1, 1.5, 1])
    
    with col_form:
        st.write("")
        st.write("")
        with st.container(border=True):
            st.subheader("🔑 Administrator Login")
            username = st.text_input("Username:")
            password = st.text_input("Password:", type="password")
            
            if st.button("Log In", use_container_width=True):
                if username and password:
                    try:
                        res = requests.post(f"{BACKEND_URL}/api/login", json={
                            "username": username.strip(),
                            "password": password
                        })
                        if res.status_code == 200:
                            st.session_state.logged_in = True
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password.")
                    except Exception as e:
                        st.error(f"Cannot connect to auth server: {e}")
                else:
                    st.warning("Please fill in all fields.")
                    
    return False