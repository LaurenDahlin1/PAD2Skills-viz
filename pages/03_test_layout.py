import streamlit as st
from streamlit_float import float_init

def example():
    float_init()

    st.write("This is the main container")

    text = ""
    for i in range(200):
        text += f"{i + 1} Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis in luctus erat, vitae accumsan elit.\n\n"
    st.write(text)

    # --- session state ---
    if "show_chat" not in st.session_state:
        st.session_state.show_chat = True
    if "messages" not in st.session_state:
        st.session_state.messages = []

    def toggle_chat():
        st.session_state.show_chat = not st.session_state.show_chat

    # --- chat history (renders ABOVE the input) ---
    if st.session_state.show_chat:
        history = st.container(height=260)
        with history:
            for m in st.session_state.messages:
                with st.chat_message(m["role"]):
                    st.write(m["content"])

    # --- bottom bar ---
    bottom_bar = st.container()
    with bottom_bar:
        # Keep a stable key so the widget doesn't change identity when the label changes
        st.button(
            "Hide" if st.session_state.show_chat else "Show",
            key="toggle_chat_btn",
            on_click=toggle_chat,
        )

        prompt = st.chat_input("Ask PADdy about jobs and skills from Project Appraisal Documents.")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append(
                {"role": "assistant", "content": f"🤖 Thanks for your question: “{prompt}”. (Test reply; no API yet.)"}
            )
            st.rerun()

        if st.session_state.show_chat:
            st.caption("Chat is in test mode (no API). Type a message and press Enter.")

    bottom_bar.float(
        "position: fixed; bottom: 0; "
        "z-index: 1000; background: white; padding: 0.75rem 1rem; "
        "border-top: 1px solid rgba(49,51,63,0.2);"
        "max-height: 60vh;"
    )

    spacer_h = 120 if st.session_state.show_chat else 70
    st.markdown(f"<div style='height:{spacer_h}px'></div>", unsafe_allow_html=True)

example()
