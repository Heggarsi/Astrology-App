import streamlit as st
import datetime as dt
from utils.auth import get_user_profile
from views.userpopup_view.user_popup import user_profile_popup


def profile_page():
    st.markdown("<h1>👤 User Profile</h1>", unsafe_allow_html=True)

    user_id = st.session_state.get("user")

    if not user_id:
        st.warning("Please login first")
        return

    # 🔹 Load existing profile
    profile = get_user_profile(user_id)

    if profile:
        st.success("Your saved profile")

        with st.form("profile_form"):

            dob = st.date_input(
                "Date of Birth",
                value=dt.date(1995, 1, 1),
                min_value=dt.date(1900, 1, 1),
                max_value=dt.date.today()
            )
            tob = st.time_input("Time of Birth", value=profile["tob"])
            place = st.text_input("Place of Birth", value=profile["place"])

            fav_color = st.selectbox(
                "Favorite Color",
                ["Red", "Yellow", "Blue", "Green", "White", "Black"],
                index=["Red", "Yellow", "Blue", "Green", "White", "Black"]
                .index(profile["fav_color"])
            )

            rashi = st.selectbox(
                "Rashi",
                [
                    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                    "Libra", "Scorpio", "Sagittarius", "Capricorn",
                    "Aquarius", "Pisces"
                ],
                index=0
            )

            language = st.selectbox(
                "Preferred Language",
                ["English", "Hindi", "Kannada", "Tamil", "Telugu"],
                index=0
            )

            gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other"],
                index=0
            )

            # 🔹 BUTTON ROW (EXTREME LEFT & RIGHT)
            col_left, col_right = st.columns([1, 1])

            with col_left:
                submit = st.form_submit_button(
                    "✅ Update Profile",
                    use_container_width=True
                )

            with col_right:
                back_to_dash = st.form_submit_button(
                    "⬅ Back To Dashboard",
                    use_container_width=True
                )

        # 🔹 HANDLE SUBMIT
        if submit:
            from utils.auth import (
                save_user_profile,
                save_user_profile_session
            )

            success = save_user_profile(
                user_id,
                str(dob),
                str(tob),
                place,
                fav_color,
                rashi,
                language,
                gender
            )

            if success:
                save_user_profile_session(
                    user_id,
                    str(dob),
                    str(tob),
                    place,
                    fav_color,
                    rashi,
                    language,
                    gender
                )

                st.success("Profile updated successfully")
                st.session_state.current_page = "dashboard"
                st.rerun()

        # 🔹 HANDLE BACK
        if back_to_dash:
            st.session_state.current_page = "dashboard"
            st.rerun()

    else:
        # 🔹 First-time user → show popup flow
        user_profile_popup()
