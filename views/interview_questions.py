import streamlit as st

import auth
from ai_engine import generate_interview_questions, AIEngineError
from parser import ParsedResume
from skills import SUPPORTED_ROLES
from utils import require_auth, page_header

require_auth()
user = auth.get_current_user()

page_header("AI TOOLS", "Interview Question Generator", "Likely questions based on your resume, skills, and target role.")

analysis = st.session_state.get("current_analysis")
if not analysis:
    st.info("Upload and analyze a resume first.")
    if st.button("Upload a Resume →"):
        st.switch_page("views/upload_resume.py")
    st.stop()

parsed_dict = analysis.get("parsed_data", {}) or {}
parsed = ParsedResume(**{k: parsed_dict.get(k) for k in ParsedResume.__dataclass_fields__})

role = st.selectbox(
    "Target role", SUPPORTED_ROLES,
    index=SUPPORTED_ROLES.index(analysis.get("role")) if analysis.get("role") in SUPPORTED_ROLES else 0,
)

if st.button("Generate Interview Questions", type="primary"):
    with st.spinner("Drafting likely interview questions..."):
        try:
            questions = generate_interview_questions(analysis["raw_text"], parsed.skills or [], role)
            st.session_state["interview_questions"] = questions
        except AIEngineError as exc:
            st.error(str(exc))

questions = st.session_state.get("interview_questions")
if questions:
    tabs = st.tabs(["🧪 Technical", "🧭 Behavioral", "🛠️ Project-Based"])
    for tab, key in zip(tabs, ["technical", "behavioral", "project_based"]):
        with tab:
            items = questions.get(key, [])
            if not items:
                st.caption("No questions generated for this category.")
            for i, q in enumerate(items, start=1):
                st.markdown(f'<div class="scan-card">{i}. {q}</div>', unsafe_allow_html=True)
                st.write("")
