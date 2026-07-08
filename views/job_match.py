import streamlit as st

import auth
import database
from semantic_matcher import match_resume_to_job
from utils import require_auth, page_header, render_gauge, render_chips, render_metric_card

require_auth()
user = auth.get_current_user()

page_header("JOB FIT", "Job Description Matcher", "Paste a job description to see how well your resume aligns.")

analysis = st.session_state.get("current_analysis")
if not analysis:
    st.info("Upload and analyze a resume first.")
    if st.button("Upload a Resume →"):
        st.switch_page("views/upload_resume.py")
    st.stop()

job_title = st.text_input("Job title (optional)", placeholder="e.g. Senior Data Analyst")
jd_text = st.text_area("Paste the job description", height=240, placeholder="Paste the full job posting here...")

if st.button("Match Resume to Job", type="primary"):
    if not jd_text.strip():
        st.error("Paste a job description first.")
    else:
        with st.spinner("Comparing your resume against this job description..."):
            result = match_resume_to_job(analysis["raw_text"], jd_text)

        st.session_state["last_job_match"] = result

        try:
            database.save_job_match(
                user_id=user["id"], access_token=user["access_token"],
                analysis_id=analysis.get("id"), job_title=job_title or "Untitled",
                job_description=jd_text, match_score=result["match_percent"],
                matching_skills=result["matching_skills"], missing_keywords=result["missing_keywords"],
            )
        except Exception as exc:
            st.warning(f"Match computed but couldn't be saved: {exc}")

if st.session_state.get("last_job_match"):
    result = st.session_state["last_job_match"]
    st.divider()

    gcol, mcol = st.columns([1, 2], gap="large")
    with gcol:
        st.markdown('<div class="scan-card">', unsafe_allow_html=True)
        render_gauge(result["match_percent"], label="JOB MATCH")
        st.markdown("</div>", unsafe_allow_html=True)
    with mcol:
        c1, c2 = st.columns(2)
        with c1:
            render_metric_card("Semantic Similarity", f"{result['semantic_score']:.0f}%")
        with c2:
            render_metric_card("Keyword Overlap", f"{result['keyword_overlap_percent']:.0f}%")

        st.progress(min(1.0, result["match_percent"] / 100))

    st.write("")
    skill_col1, skill_col2 = st.columns(2, gap="large")
    with skill_col1:
        st.markdown('<div class="eyebrow">MATCHING SKILLS</div>', unsafe_allow_html=True)
        render_chips(result["matching_skills"], kind="match")
    with skill_col2:
        st.markdown('<div class="eyebrow">MISSING KEYWORDS</div>', unsafe_allow_html=True)
        render_chips(result["missing_keywords"], kind="missing")
