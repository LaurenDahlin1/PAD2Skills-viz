import streamlit as st
from streamlit_float import float_init

def example(chat_placeholder: str = "Ask a question..."):
    float_init()

    st.write("This is the main container")

    text = ""
    for i in range(100):
        text += (
            f"{i + 1} Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Duis in luctus erat, vitae accumsan elit.\n\n"
        )
    st.write(text)

    # --- session state init ---
    if "show_chat" not in st.session_state:
        st.session_state.show_chat = True
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None  # set by pills

    def toggle_chat():
        st.session_state.show_chat = not st.session_state.show_chat

    # --- preset question pills ---
    if st.button("Why is the sky blue?"):
        st.session_state.pending_prompt = "Why is the sky blue?"
        st.session_state.show_chat = True

    if st.button("Why is the grass green?"):
        st.session_state.pending_prompt = "Why is the grass green?"
        st.session_state.show_chat = True

    # --- consume pending prompt (from pill) ---
    if st.session_state.pending_prompt:
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append(
            {"role": "assistant", "content": f"Thanks for your question: {prompt}. (Test reply; no API yet.)"}
        )
        st.rerun()

    has_any_messages = len(st.session_state.messages) > 0

    # --- chat history ---
    if st.session_state.show_chat and has_any_messages:
        history = st.container(height=300)
        with history:
            for m in st.session_state.messages:
                with st.chat_message(m["role"]):
                    st.write(m["content"])
            st.markdown('###')

    # --- bottom bar ---
    bottom_bar = st.container()
    with bottom_bar:
        if has_any_messages:
            col_left, col_right = st.columns([8, 1])
            with col_left:
                prompt = st.chat_input(chat_placeholder, key="chat_input")
            with col_right:
                st.button(
                    label="",
                    icon=":material/keyboard_double_arrow_down:"
                    if st.session_state.show_chat
                    else ":material/keyboard_double_arrow_up:",
                    key="toggle_chat_btn",
                    type="tertiary",
                    on_click=toggle_chat,
                    use_container_width=False,
                )
        else:
            prompt = st.chat_input(chat_placeholder, key="chat_input")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append(
                {"role": "assistant", "content": f"Thanks for your question: {prompt}. (Test reply; no API yet.)"}
            )
            st.rerun()

    bottom_bar.float(
        "position: fixed; bottom: 0; "
        "z-index: 1000; background: white; padding: 0.75rem 1rem; "
        "border-top: 1px solid rgba(49,51,63,0.2);"
        "padding-bottom: 7px;"
        "max-height: 50vh;"
    )

example("Ask a question in the chat...")