import streamlit as st
from pathlib import Path
from utils.extension import get_astro_response, improve_prompt


# ---------- LOAD CSS ----------
def load_css():
    css = Path(__file__).with_suffix(".css")
    with open(css) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ---------- DYNAMIC TEXTAREA HEIGHT ----------
def calculate_textarea_height(
    text: str,
    min_height: int = 90,
    max_height: int = 290,
    chars_per_line: int = 60,
    line_height: int = 13,
) -> int:
    if not text:
        return min_height

    lines = text.count("\n") + (len(text) // chars_per_line) + 1
    height = lines * line_height

    return max(min_height, min(height, max_height))


def astrology_dashboard(logout_callback):
    load_css()

    # ---------- SESSION INIT ----------
    st.session_state.setdefault("current_page", "dashboard")
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("show_suggestions", True)
    st.session_state.setdefault("suggestion_set", 0)
    st.session_state.setdefault("pending_prompt", None)
    st.session_state.setdefault("improved_prompt", None)
    st.session_state.setdefault("prompt_input", "")
    st.session_state.setdefault("reset_prompt", False)
    st.session_state.setdefault("improve_version", 0)
    st.session_state.setdefault("menu_reset", False)
    

    # ---------- SAFE RESET ----------
    if st.session_state.reset_prompt:
        st.session_state.prompt_input = ""
        st.session_state.reset_prompt = False

    # ---------- SUGGESTIONS ----------
    SUGGESTIONS = [
        [
        "🧘 Daily Horoscope Prediction",
        "💍 Marriage Compatibility Astrology",
        "💼 Career Astrology Guidance",
        "🌙 Moon Sign Astrology Meaning",
        "🪐 Planetary Dosha Analysis"
    ],
    [
        "📈 Business Astrology Prediction",
        "❤️ Love Life Astrology Prediction",
        "🏡 Property Yoga in Kundali",
        "🧿 Rahu–Ketu Dosha Effects",
        "🔮 Lucky Colors as per Astrology"
    ],
    [
        "🌟 Career Growth as per Kundali",
        "💰 Wealth Yoga in Horoscope",
        "💏 Relationship Compatibility Astrology",
        "🕉️ Spiritual Path as per Horoscope",
        "🌌 Planet Positions in Birth Chart"
    ],
    ]

    current_suggestions = SUGGESTIONS[
        st.session_state.suggestion_set % len(SUGGESTIONS)
    ]

    # ================= SIDEBAR =================
    st.sidebar.title("☰ Menu")
    if st.session_state.menu_reset:
        st.session_state.sidebar_menu = "— Select —"
        st.session_state.menu_reset = False

    menu_action = st.sidebar.selectbox(
        "Choose an option",
        ["— Select —", "🧹 Clear Chat", "👤 Profile", "🚪 Logout"],
        key="sidebar_menu",
        label_visibility="collapsed"
    )

    if menu_action == "🧹 Clear Chat":
        st.session_state.messages.clear()
        st.session_state.show_suggestions = True
        st.session_state.suggestion_set = 0
        st.session_state.improved_prompt = None
        st.session_state.pending_prompt = None
        st.session_state.reset_prompt = True
        st.session_state.menu_reset = True        
        st.rerun()

    elif menu_action == "👤 Profile":      
        st.session_state.current_page = "profile"  
        st.session_state.menu_reset = True
        st.rerun()
    elif menu_action == "🚪 Logout":     
        st.session_state.current_page = "dashboard"   
        st.session_state.messages.clear()
        st.session_state.show_suggestions = True
        st.session_state.suggestion_set = 0
        st.session_state.improved_prompt = None
        st.session_state.pending_prompt = None
        st.session_state.reset_prompt = True
        st.session_state.improve_version=0    
        st.session_state.menu_reset = True    
        logout_callback()
        st.rerun()

    # if st.sidebar.button("🧹 Clear Chat"):
    #     st.session_state.messages.clear()
    #     st.session_state.show_suggestions = True
    #     st.session_state.suggestion_set = 0
    #     st.session_state.improved_prompt = None
    #     st.session_state.pending_prompt = None
    #     st.session_state.reset_prompt = True
    #     st.rerun()

    st.sidebar.title("🔮 Chat History")

    if not st.session_state.messages:
        st.sidebar.info("No conversations yet")
    else:
        for msg in st.session_state.messages[-10:]:
            icon = "🧑" if msg["role"] == "user" else "🤖"
            preview = msg["content"][:40] + "..."
            st.sidebar.markdown(
                f"<div class='sidebar-msg'>{icon} {preview}</div>",
                unsafe_allow_html=True
            )

    # st.sidebar.markdown("---")
    # st.sidebar.button("🚪 Logout", on_click=logout_callback)

    # ================= MAIN =================
    st.markdown(
        "<h1 class='dashboard-title'>🔮 Ask Your Astrology Question</h1>",
        unsafe_allow_html=True
    )

    # ---------- CHAT ----------
    for msg in st.session_state.messages:
        css = "chat-user" if msg["role"] == "user" else "chat-bot"
        st.markdown(
            f"<div class='{css}'>{msg['content']}</div>",
            unsafe_allow_html=True
        )

    # ---------- PROMPT BAR ----------
    st.markdown("<div class='prompt-parent'>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([6,0.4,0.3])

    with c1:
        user_input = st.text_input(
            "",
            placeholder="Ask about marriage, career, kundali dosha...",
            key="prompt_input",
            label_visibility="collapsed"
        )

    with c2:
        send = st.button("Send")

    with c3:
        improve = st.button("↺")

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------- IMPROVE ----------
    if improve:
        if not user_input.strip():
            st.warning("✍️ Please type something to improve.")
        else:
            with st.spinner("✨ Improving your prompt..."):
                st.session_state.improved_prompt = improve_prompt(user_input)
            st.session_state.improve_version += 1
            st.rerun()

    # ---------- IMPROVED PROMPT UI ----------
    if st.session_state.improved_prompt:
        st.markdown("<div class='improve-box'>", unsafe_allow_html=True)
        st.markdown("✨ **Your prompt could be improved like this:**")

        dynamic_height = calculate_textarea_height(
            st.session_state.improved_prompt
        )
        
        improved_text = st.text_area(
            "",
            value=st.session_state.improved_prompt,
            height=dynamic_height,
            key=f"improved_prompt_editor_{st.session_state.improve_version}"
        )
        

        if st.button("Send Improved Prompt"):
            st.session_state.pending_prompt = improved_text
            st.session_state.improved_prompt = None
            st.session_state.reset_prompt = True
            st.session_state.improve_version += 1  # reset editor
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- SEND NORMAL ----------
    if send and user_input.strip():
        st.session_state.pending_prompt = user_input
        st.session_state.improved_prompt = None
        st.session_state.reset_prompt = True
        st.rerun()

    # ---------- SUGGESTIONS ----------
    if st.session_state.show_suggestions:
        st.markdown(
            "<h3 class='suggestion-title'>✨ Suggested Topics</h3>",
            unsafe_allow_html=True
        )
        cols = st.columns(5)

        for i, col in enumerate(cols):
            with col:
                if st.button(current_suggestions[i], key=f"suggestion_{i}"):
                    st.session_state.pending_prompt = current_suggestions[i]
                    st.session_state.improved_prompt = None
                    st.session_state.show_suggestions = False
                    st.session_state.reset_prompt = True
                    st.rerun()

    # ---------- PROCESS PROMPT ----------
    if st.session_state.pending_prompt:
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None

        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )

        with st.spinner("🔮 Reading your stars..."):
            reply = get_astro_response(prompt,st.session_state.user)

        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )

        st.session_state.suggestion_set += 1
        st.session_state.show_suggestions = True

        st.rerun()
