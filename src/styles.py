"""Shared CSS styles for mobile-first Streamlit UI."""

import streamlit as st

# Mobile-first CSS
MOBILE_CSS = """
<style>

/* Safe zone for mobile notches and status bars */
.block-container { 
    padding-top: max(3rem, env(safe-area-inset-top)); 
    padding-bottom: 3rem;
    padding-left: env(safe-area-inset-left);
    padding-right: env(safe-area-inset-right);
}

h1 { 
    font-size: 1.6rem; 
    margin-top: 1rem; 
    font-weight: 600;
    letter-spacing: -0.02em;
    color: #1a1a1a;
}

h2 { 
    font-size: 1.25rem; 
    font-weight: 600;
    letter-spacing: -0.01em;
    color: #2a2a2a;
}

h3 { 
    font-size: 1.05rem; 
    font-weight: 600;
    color: #3a3a3a;
}

/* Better body text */
p, div, span {
    color: #4a4a4a;
    line-height: 1.6;
    font-weight: 400;
}

div[data-testid="stVerticalBlock"] > div { width: 100%; }

/* Chatbot output box styling */
.chatbot-box {
    background-color: #f0f2f6;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1.5rem;
    font-size: 0.95rem;
    line-height: 1.6;
    color: #2a2a2a;
}

.chatbot-emoji {
    font-size: 1.5em;
    vertical-align: middle;
    margin-right: 0.5rem;
}

/* Reduce spacing around selectors */
div[data-testid="stSelectbox"] {
    margin-bottom: 0.5rem;
}

/* Reduce top padding on plotly charts */
div[data-testid="stPlotlyChart"] {
    margin-top: -0.5rem;
}

/* Better button styling */
button {
    font-weight: 500;
    letter-spacing: 0.01em;
}

/* Better caption styling */
.caption {
    font-size: 0.875rem;
    color: #6a6a6a;
    font-weight: 400;
}

/* Prevent auto-scroll to chat input on load */
div[data-testid="stChatInput"] {
    scroll-margin-top: 0;
}

@media (max-width: 640px) {
  .block-container { 
    padding-left: max(0.75rem, env(safe-area-inset-left)); 
    padding-right: max(0.75rem, env(safe-area-inset-right)); 
  }
  h1 { font-size: 1.35rem; }
  .chatbot-box { font-size: 0.9rem; }
}
</style>
"""


def inject_custom_css():
    """Inject custom CSS into the Streamlit app."""
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)
