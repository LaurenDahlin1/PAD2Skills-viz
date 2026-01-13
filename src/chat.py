"""Modular floating chat bottom bar for PAD2Skills pages.

Usage on a page:

from chat_bar import render_floating_chat

# In your page code (after main content):
render_floating_chat(
    chat_placeholder="Ask PADdy a question...",
    on_message_callback=lambda msg: f"Echo: {msg}"
)

# For pill buttons somewhere else:
from chat_bar import handle_preset_question
if st.button("Example pill"):
    handle_preset_question("Example pill")
"""

from __future__ import annotations

from typing import Callable, Optional
import streamlit as st
from streamlit_float import float_init


# -----------------------------
# Session state helpers
# -----------------------------
def init_chat_session_state() -> None:
    """Initialize chat-related session state variables."""
    if "show_chat" not in st.session_state:
        st.session_state.show_chat = True
    if "messages" not in st.session_state:
        st.session_state.messages = []  # [{"role": "user"/"assistant", "content": str}]
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None  # str|None


def handle_preset_question(question: str) -> None:
    """Queue a preset question (pill) to be processed on next render."""
    init_chat_session_state()
    st.session_state.pending_prompt = question
    st.session_state.show_chat = True


# -----------------------------
# Main render function
# -----------------------------
def render_chat_bottom_bar(
    chat_placeholder: str = "Ask a question...",
    on_message_callback: Optional[Callable[[str], str]] = None,
    history_height: int = 300,
) -> None:
    """
    Render chat history (above) + floating bottom bar input (fixed).

    Key layout rule:
    - History is rendered BEFORE the floated footer.
    - Footer contains ONLY the input + toggle, so history can’t overlap it.
    """
    float_init()
    init_chat_session_state()

    def toggle_chat() -> None:
        st.session_state.show_chat = not st.session_state.show_chat

    def get_response(user_text: str) -> str:
        if on_message_callback:
            return on_message_callback(user_text)
        return f"Thanks for your question: {user_text}. (Test reply; no API yet.)"

    # If a pill set a pending prompt, consume it first and rerun
    if st.session_state.pending_prompt:
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": get_response(prompt)})
        st.rerun()

    has_any_messages = len(st.session_state.messages) > 0

    # -----------------------------
    # Chat history (FLOAT it so it doesn't appear in page flow)
    # -----------------------------
    history = st.container()
    if st.session_state.show_chat and has_any_messages:
        with history:
            history_box = st.container(height=history_height)
            with history_box:
                for m in st.session_state.messages:
                    with st.chat_message(m["role"]):
                        st.write(m["content"])
                st.markdown('###')

        # Float history above the footer
        history.float(
            "position: fixed; "
            "bottom: 50px; "
            "z-index: 999; "
            "background: white; "
            "padding: 0.5rem 1rem; "
        )

    # -----------------------------
    # Floating footer (ONLY input + toggle)
    # -----------------------------
    footer = st.container()
    with footer:
        # Toggle appears only after first message (matches your earlier behavior)
        if has_any_messages:
            col_left, col_right = st.columns([6, 1])
            with col_left:
                prompt = st.chat_input(chat_placeholder, key="chat_input")
            with col_right:
                st.button(
                    label="",
                    icon=(
                        ":material/keyboard_double_arrow_down:"
                        if st.session_state.show_chat
                        else ":material/keyboard_double_arrow_up:"
                    ),
                    key="toggle_chat_btn",
                    type="tertiary",
                    on_click=toggle_chat,
                    use_container_width=False,
                )
        else:
            col_left, col_right = st.columns([6, 1])
            with col_left:
                prompt = st.chat_input(chat_placeholder, key="chat_input")
            with col_right:
                st.write("")  # Empty to keep alignment

        if prompt:
            # Always show chat history after submit
            st.session_state.show_chat = True

            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append({"role": "assistant", "content": get_response(prompt)})
            st.rerun()

    # Float the footer
    footer.float(
        "position: fixed; bottom: 0; "
        "z-index: 1000; background: white; padding: 0.75rem 1rem; "
        "border-top: 1px solid rgba(49,51,63,0.2);"
        "padding-bottom: 7px;"
    )
