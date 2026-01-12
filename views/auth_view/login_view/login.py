import streamlit as st
from utils.auth import verify_user
from pathlib import Path

def load_css(path):
    with open(path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def login_page():
    load_css(Path(__file__).with_suffix(".css"))

    st.markdown('<h1>Welcome Back</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Sign in to continue</p>', unsafe_allow_html=True)

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login = st.form_submit_button("Login")

    if login:
        if not email or not password:
            st.error("Please fill all fields")
        elif (user_id := verify_user(email, password)):
            st.session_state.user = user_id            
            st.session_state.user_email = email.lower()
            st.rerun()
        else:
            st.error("Invalid credentials")


    st.markdown('<div class="links">', unsafe_allow_html=True)
    col1, col2 = st.columns([7,1])
    with col1:
        if st.button("Register"):
            st.session_state.page = "register"
            st.rerun()
    with col2:      
        if st.button("Forgot Password?", key="forgot_password_btn"):
            st.session_state.page = "forgot"
            st.rerun()        
    st.markdown('</div></div>', unsafe_allow_html=True)
