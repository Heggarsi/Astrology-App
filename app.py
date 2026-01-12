import streamlit as st
from utils.auth import init_db,init_profile_table,is_user_profile_complete

init_db()
init_profile_table()


st.set_page_config(page_title="Astro App", page_icon="🔮", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "login"

if "user" not in st.session_state:
    st.session_state.user = 0



def logout():
    st.session_state.user = 0
    st.session_state.page = "login"
    
#st.session_state.user = 1

if st.session_state.user:       

    if not is_user_profile_complete(st.session_state.user):
        from views.userpopup_view.user_popup import user_profile_popup
        user_profile_popup()
    else:
        # ---------- PAGE ROUTER (AFTER PROFILE COMPLETE) ----------
        from views.dashboard_view.dashboard import astrology_dashboard
        from views.profile_view.profile import profile_page

        current_page = st.session_state.get("current_page", "dashboard")

        if current_page == "profile":
            profile_page()
        else:
            astrology_dashboard(logout)

else:
    if st.session_state.page == "login":
        from views.auth_view.login_view.login import login_page
        login_page()
    elif st.session_state.page == "register":
        from views.auth_view.register_view.register import register_page
        register_page()
    elif st.session_state.page == "forgot":
        from views.auth_view.forgot_password_view.forgot_password import forgot_password_page
        forgot_password_page()





# import streamlit as st
# from auth import init_db

# init_db()

# st.set_page_config(page_title="Astro App", page_icon="🔮", layout="wide")

# if "page" not in st.session_state:
#     st.session_state.page = "login"

# if "user" not in st.session_state:
#     st.session_state.user = None

# if "profile_done" not in st.session_state:
#     st.session_state.profile_done = False


# def logout():
#     st.session_state.user = None
#     st.session_state.page = "login"
#     st.session_state.profile_done = False
#     st.rerun()


# if st.session_state.user:
#     if not st.session_state.profile_done:
#         from views.dashboard_view.user_popup import user_profile_popup
#         user_profile_popup()
#     else:
#         from views.dashboard_view.dashboard import astrology_dashboard
#         astrology_dashboard(logout)
# else:
#     if st.session_state.page == "login":
#         from views.auth_view.login_view.login import login_page
#         login_page()
#     elif st.session_state.page == "register":
#         from views.auth_view.register_view.register import register_page
#         register_page()
#     elif st.session_state.page == "forgot":
#         from views.auth_view.forgot_password_view.forgot_password import forgot_password_page
#         forgot_password_page()
