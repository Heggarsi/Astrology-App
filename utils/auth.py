"""
Simple authentication backend using SQLite and secure password hashing (sha256 + salt).
This is intentionally lightweight for demo purposes only — do NOT use in production.
"""

"""
Explanation of imported libraries and code examples of their usage in this file:


import sqlite3
    - Usefulness: Provides a lightweight disk-based database. Used here to store user credentials, manage user-related tables, and run SQL queries.
    - Example:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE email = ?", (email,))


import hashlib
    - Usefulness: Provides secure hash functions. Used for hashing passwords (in combination with a salt) so that raw passwords are never stored in the database.
    - Example:
        salt = secrets.token_hex(16)
        h = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


import secrets
    - Usefulness: Provides functions for generating cryptographically secure random numbers and strings. Used to generate unique salts and password reset tokens.
    - Example:
        salt = secrets.token_hex(16)
        reset_token = secrets.token_urlsafe(32)


import time
    - Usefulness: Time access and conversions. Used for storing and checking reset token expiration timestamps.
    - Example:
        expiry = int(time.time()) + 600  # Sets expiry to 10 minutes from now


from typing import Optional, Tuple
    - Usefulness: Type hints to clarify expected argument and return types. "Optional" is used for arguments that can be None, while "Tuple" describes multi-value returns.
    - Example:
        def _hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
            ...
"""

"""
Other useful Python standard library imports for authentication, web, and app development:

import os
    - Usefulness: Interacts with the operating system. Useful for reading environment variables (like API keys), manipulating file paths, or checking file existence.
    - Example:
        secret_key = os.environ.get("SECRET_KEY")
        path = os.path.join("data", "users.db")

import json
    - Usefulness: For encoding and decoding JSON data. Handy for config files, API responses, or exchanging data with JavaScript.
    - Example:
        with open("config.json") as f:
            config = json.load(f)

import datetime
    - Usefulness: Provides date and time manipulation, e.g., for generating time-based tokens, timestamps, or expiry calculations.
    - Example:
        expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)

import logging
    - Usefulness: Flexible framework for emitting log messages from apps. Recommended over print statements for tracking errors and events.
    - Example:
        logging.basicConfig(level=logging.INFO)
        logging.info("User logged in successfully")

import functools
    - Usefulness: Higher-order functions for wrapping (decorating) other functions, such as to enforce authentication before allowing access to a function.
    - Example:
        @functools.lru_cache(maxsize=128)
        def get_user(id):
            ...

import base64
    - Usefulness: Encoding and decoding binary data in Base64, handy for basic token formats or image embedding.
    - Example:
        encoded = base64.b64encode(b"secret data").decode("utf-8")

import smtplib
    - Usefulness: Sending emails via SMTP; useful for implementing password reset, notifications, etc.
    - Example:
        with smtplib.SMTP("smtp.example.com") as server:
            server.sendmail(from_addr, to_addrs, msg)
"""


import streamlit as st
import sqlite3
import hashlib
import secrets
import time
from typing import Optional, Tuple


DB_PATH = "users.db"


def get_conn():   
    # with(connect(host="127.0.0.1",
    #              user="root",
    #              password="Ghjk!@123",
    #              database="astrology_app")
    #     as conn):     
    #     st.warning("connection done")
    return sqlite3.connect(DB_PATH)
    
    print("connection created")


def init_db() -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                email TEXT UNIQUE,
                password_hash TEXT,
                salt TEXT,
                reset_token TEXT,
                reset_token_expiry INTEGER
            )
            """
        )
        conn.commit()

# ==========================================================
# USER PROFILE STORAGE
# ==========================================================

def init_profile_table() -> None:
    with get_conn() as conn:
        cur = conn.cursor()        
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                dob TEXT,
                tob TEXT,
                place TEXT,
                fav_color TEXT,
                rashi TEXT,
                language TEXT,
                gender TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        conn.commit()

def save_user_profile(   
    user_id: int,
    dob: str,
    tob: str,
    place: str,
    fav_color: str,
    rashi: str,
    language: str,
    gender: str,
) -> bool:
    """
    Saves user profile to database.
    Returns True if successful, False otherwise.
    """
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO user_profiles
                (user_id, dob, tob, place, fav_color, rashi, language, gender)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    dob = excluded.dob,
                    tob = excluded.tob,
                    place = excluded.place,
                    fav_color = excluded.fav_color,
                    rashi = excluded.rashi,
                    language = excluded.language,
                    gender = excluded.gender
                """,
                (user_id, dob, tob, place, fav_color, rashi, language, gender),
            )
            conn.commit()
        return True
    except Exception as e:
        # Optional: log the error
        print(f"Error saving profile: {e}")
        return False


def save_user_profile_session(
    user_id: int,
    dob: str,
    tob: str,
    place: str,
    fav_color: str,
    rashi: str,
    language: str,
    gender: str,
) -> None:
    """
    Stores ONLY the current user's profile in session.
    """
    st.session_state.user_profile = {
        "user_id": user_id,
        "dob": dob,
        "tob": tob,
        "place": place,
        "fav_color": fav_color,
        "rashi": rashi,
        "language": language,
        "gender": gender,
    }

def get_user_profile(user_id: int) -> dict | None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT dob, tob, place, fav_color, rashi, language, gender
            FROM user_profiles
            WHERE user_id = ?
            """,
            (user_id,),
        )
        row = cur.fetchone()

    if not row:
        return None

    return {
        "dob": row[0],
        "tob": row[1],
        "place": row[2],
        "fav_color": row[3],
        "rashi": row[4],
        "language": row[5],
        "gender": row[6],
    }

def get_user_profile_session(user_id: int) -> dict | None:
    """
    Returns the current user's profile from session_state.
    Falls back to None if not available or mismatched user.
    """
    profile = st.session_state.get("user_profile")

    if not profile:
        return None

    if profile.get("user_id") != user_id:
        return None

    return {
        "dob": profile.get("dob"),
        "tob": profile.get("tob"),
        "place": profile.get("place"),
        "fav_color": profile.get("fav_color"),
        "rashi": profile.get("rashi"),
        "language": profile.get("language"),
        "gender": profile.get("gender"),
    }

def get_user_profile_smart(user_id: int) -> dict | None:
    """
    Smart profile retrieval: checks session first, then DB, then caches in session.
    Returns None if profile doesn't exist.
    """
    # Try to get from session first
    profile = get_user_profile_session(user_id)    
    if profile:
        st.warning("hi")
        return profile
    
    # If not in session, fetch from database
    profile = get_user_profile(user_id)    
    if not profile:
        st.warning("hello")
        return None
    
    # Cache the profile in session for future use
    save_user_profile_session(
        user_id=user_id,
        dob=profile["dob"],
        tob=profile["tob"],
        place=profile["place"],
        fav_color=profile["fav_color"],
        rashi=profile["rashi"],
        language=profile["language"],
        gender=profile["gender"],
    )
    
    return profile   

def is_user_profile_complete(user_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT 1
            FROM user_profiles
            WHERE user_id = ?
            """,
            (user_id,),
        )
        return cur.fetchone() is not None


def _hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return salt, h


def create_user(username: str, email: str, password: str) -> bool:
    salt, pw_hash = _hash_password(password)
    #breakpoint()
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)",
                (username, email.lower(), pw_hash, salt),
            )
            conn.commit()
        return True
    except Exception:
        return False


def verify_user(email: str, password: str) -> Optional[int]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, password_hash, salt FROM users WHERE email = ?",
            (email.lower(),)
        )
        row = cur.fetchone()
        if not row:
            return None

        user_id, stored_hash, salt = row
        _, computed_hash = _hash_password(password, salt)

        if computed_hash == stored_hash:
            return user_id
        return 0



def generate_reset_token(email: str, ttl_seconds: int = 3600) -> Optional[str]:
    token = secrets.token_urlsafe(32)
    expiry = int(time.time()) + ttl_seconds
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = ?", (email.lower(),))
        row = cur.fetchone()
        if not row:
            return None
        cur.execute(
            "UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE email = ?",
            (token, expiry, email.lower()),
        )
        conn.commit()
    return token


def verify_reset_token(email: str, token: str) -> bool:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT reset_token, reset_token_expiry FROM users WHERE email = ?",
            (email.lower(),),
        )
        row = cur.fetchone()
        if not row:
            return False
        stored_token, expiry = row
        if stored_token != token:
            return False
        if expiry is None:
            return False
        if int(time.time()) > expiry:
            return False
        return True


def reset_password(email: str, token: str, new_password: str) -> bool:
    if not verify_reset_token(email, token):
        return False
    salt, pw_hash = _hash_password(new_password)
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET password_hash = ?, salt = ?, reset_token = NULL, reset_token_expiry = NULL WHERE email = ?",
            (pw_hash, salt, email.lower()),
        )
        conn.commit()
    return True


def user_exists(email: str) -> bool:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE email = ?", (email.lower(),))
        return cur.fetchone() is not None
