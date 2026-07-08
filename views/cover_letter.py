import streamlit as st

import auth
from ai_engine import generate_cover_letter, AIEngineError
from utils import require_auth, page_header

require_auth()
user = auth.get_current_user()

page_header("AI TOOLS", "Cover Letter Generator", "Generated from your resume, the target role, and (optionally) a job description.")

analysis = st.session_state.get("current_analysis")
if not analysis:
    st.info("Upload and analyze a resume first.")
    if st.button("Upload a Resume →"):
        st.switch_page("views/upload_resume.py")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    role = st.text_input("Target role", value=analysis.get("role") or "")
with col2:
    company_name = st.text_input("Company name (optional)", placeholder="e.g. Acme Corp")

job_description = st.text_area("Job description (optional, improves relevance)", height=160)

if st.button("Generate Cover Letter", type="primary"):
    with st.spinner("Writing your cover letter..."):
        try:
            letter = generate_cover_letter(
                analysis["raw_text"], role=role or "the target role",
                job_description=job_description, company_name=company_name,
            )
            st.session_state["cover_letter_text"] = letter
        except AIEngineError as exc:
            st.error(str(exc))

if st.session_state.get("cover_letter_text"):
    st.divider()
    st.markdown('<div class="eyebrow">YOUR COVER LETTER (click to copy)</div>', unsafe_allow_html=True)
    st.code(st.session_state["cover_letter_text"], language=None)
    st.download_button(
        "Download as .txt", data=st.session_state["cover_letter_text"],
        file_name="cover_letter.txt", mime="text/plain",
    )
