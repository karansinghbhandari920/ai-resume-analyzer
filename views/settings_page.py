import os

import streamlit as st

import auth
from skills import SUPPORTED_ROLES
from utils import require_auth, page_header

require_auth()
user = auth.get_current_user()

page_header("ACCOUNT", "Settings", "Preferences and connection status.")

st.markdown('<div class="eyebrow">PREFERENCES</div>', unsafe_allow_html=True)
default_role = st.selectbox(
    "Default target role for new uploads", SUPPORTED_ROLES,
    index=SUPPORTED_ROLES.index(st.session_state.get("selected_role", SUPPORTED_ROLES[0])),
)
if st.button("Save Preference"):
    st.session_state["selected_role"] = default_role
    st.success("Saved for this session.")

st.write("")
st.markdown('<div class="eyebrow">CONNECTION STATUS</div>', unsafe_allow_html=True)
checks = [
    ("Supabase URL", bool(os.environ.get("SUPABASE_URL"))),
    ("Supabase Anon Key", bool(os.environ.get("SUPABASE_ANON_KEY"))),
    ("Gemini API Key", bool(os.environ.get("GEMINI_API_KEY"))),
]
for label, ok in checks:
    icon = "🟢" if ok else "🔴"
    status = "Configured" if ok else "Missing - add it to your .env file"
    st.write(f"{icon} **{label}:** {status}")

st.write("")
st.markdown('<div class="eyebrow">SESSION</div>', unsafe_allow_html=True)
if st.button("Clear Loaded Resume From This Session"):
    st.session_state["current_analysis"] = None
    st.session_state["current_analysis_id"] = None
    st.session_state["chat_messages"] = []
    st.success("Cleared. Your saved history in Supabase is unaffected.")
