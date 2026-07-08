import streamlit as st

import auth
import database
from ai_engine import chatbot_response, AIEngineError
from utils import require_auth, page_header

require_auth()
user = auth.get_current_user()

page_header("AI TOOLS", "Resume Chatbot", "Ask anything about your resume, ATS score, or role fit.")

analysis = st.session_state.get("current_analysis")
if not analysis:
    st.info("Upload and analyze a resume first so the chatbot has context to work with.")
    if st.button("Upload a Resume →"):
        st.switch_page("views/upload_resume.py")
    st.stop()

analysis_id = analysis.get("id")

# Load history once per analysis
if st.session_state.get("chat_loaded_for") != analysis_id:
    st.session_state["chat_messages"] = []
    if analysis_id:
        try:
            history = database.get_chat_history(user["id"], user["access_token"], analysis_id)
            st.session_state["chat_messages"] = [
                {"role": h["role"], "message": h["message"]} for h in history
            ]
        except Exception:
            pass
    st.session_state["chat_loaded_for"] = analysis_id


def _send(message: str) -> None:
    st.session_state["chat_messages"].append({"role": "user", "message": message})
    try:
        reply = chatbot_response(message, analysis, st.session_state["chat_messages"])
    except AIEngineError as exc:
        reply = f"⚠️ {exc}"
    st.session_state["chat_messages"].append({"role": "assistant", "message": reply})
    if analysis_id:
        try:
            database.save_chat_message(user["id"], user["access_token"], analysis_id, "user", message)
            database.save_chat_message(user["id"], user["access_token"], analysis_id, "assistant", reply)
        except Exception:
            pass


if not st.session_state["chat_messages"]:
    st.markdown('<div class="eyebrow">TRY ASKING</div>', unsafe_allow_html=True)
    suggestions = [
        "How can I improve my ATS score?",
        "Which skills am I missing?",
        "Which role suits me best?",
        "How can I improve my resume?",
    ]
    cols = st.columns(len(suggestions))
    for col, suggestion in zip(cols, suggestions):
        if col.button(suggestion, use_container_width=True):
            with st.spinner("Thinking..."):
                _send(suggestion)
            st.rerun()

for msg in st.session_state["chat_messages"]:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.write(msg["message"])

prompt = st.chat_input("Ask about your resume...")
if prompt:
    with st.spinner("Thinking..."):
        _send(prompt)
    st.rerun()
