import streamlit as st
import re
from utils.auth import generate_reset_token, reset_password
from pathlib import Path

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def load_css(path):
    with open(path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def forgot_password_page():
    load_css(Path(__file__).with_suffix(".css"))

    st.markdown('<h1>Reset Password</h1>', unsafe_allow_html=True)

    with st.form("token_form"):
        email = st.text_input("Email")
        generate = st.form_submit_button("Generate Token")

    if generate:
        token = generate_reset_token(email)
        if token:
            st.info(f"Token (demo): {token}")
        else:
            st.error("Email not found")

    st.markdown("<hr>", unsafe_allow_html=True)

    with st.form("reset_form"):
        email2 = st.text_input("Email")
        token = st.text_input("Token")
        pw1 = st.text_input("New Password", type="password")
        pw2 = st.text_input("Confirm Password", type="password")
        reset = st.form_submit_button("Reset Password")

    if reset:
        if pw1 != pw2:
            st.error("Passwords do not match")
        elif reset_password(email2, token, pw1):
            st.success("Password updated")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("Invalid token")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
