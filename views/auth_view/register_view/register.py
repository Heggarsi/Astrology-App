import streamlit as st
# The 're' library is used for regular expressions in Python.
# It provides a way to search, find, and manipulate text using patterns.
# In this code, it is used to validate email addresses using a regular expression.
# The EMAIL_REGEX variable is a compiled regular expression that matches email addresses.
# It checks if an email address contains an @ symbol and a dot after it, ensuring it's a valid email format.
import re
from utils.auth import create_user, user_exists
# The 'pathlib' library provides a way to flexibly construct and inspect file paths.
# In this code, it is used to get the path of the CSS file that matches the current Python file name,
# i.e., if the file is 'register.py', then Path(__file__).with_suffix('.css') yields 'register.css'.
# This ensures that when there are multiple CSS files, only the CSS file with the same base name as this Python file
# (i.e., 'register.css' for 'register.py') is selected and loaded, keeping style management modular and specific.
from pathlib import Path

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def load_css(path):
    with open(path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def register_page():
    load_css(Path(__file__).with_suffix(".css"))

    st.markdown('<h1>Create Account</h1>', unsafe_allow_html=True)

    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Register")

    if submit:
        if not all([username, email, password, confirm]):
            st.error("All fields required")
        elif not EMAIL_REGEX.match(email):
            st.error("Invalid email")
        elif password != confirm:
            st.error("Passwords do not match")
        elif user_exists(email):
            st.error("User already exists")
        elif create_user(username, email, password):
            st.success("Account created")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("Registration failed")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
