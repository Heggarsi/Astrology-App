import streamlit as st
import datetime as dt
from utils.auth import save_user_profile,save_user_profile_session

def user_profile_popup():
    st.title("🔮 Tell Us About You")

    with st.form("profile_form"):
        dob = st.date_input(
            "Date of Birth",
            value=dt.date(1995, 1, 1),
            min_value=dt.date(1900, 1, 1),
            max_value=dt.date.today()
        )

        tob = st.time_input("Time of Birth")
        place = st.text_input("Place of Birth")
        fav_color = st.selectbox(
            "Favorite Color",
            ["Red", "Yellow", "Blue", "Green", "White", "Black"]
        )
        rashi = st.selectbox(
            "Rashi (optional)",
            ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn",
             "Aquarius", "Pisces"]
        )
        language = st.selectbox(
            "Preferred Language",
            ["English", "Hindi", "Kannada", "Tamil", "Telugu"]
        )
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])

        submit = st.form_submit_button("Continue")

    if submit:
        user_id = st.session_state.get("user")  # set during login

        success = save_user_profile(
            user_id=user_id,
            dob=str(dob),
            tob=str(tob),
            place=place,
            fav_color=fav_color,
            rashi=rashi,
            language=language,
            gender=gender,
        )
    
        if success:
            save_user_profile_session(
                user_id=user_id,
                dob=str(dob),
                tob=str(tob),
                place=place,
                fav_color=fav_color,
                rashi=rashi,
                language=language,
                gender=gender,
            )
            st.success("Profile saved successfully")
            st.rerun()
        else:
            st.error("Failed to save profile. Please try again.")
