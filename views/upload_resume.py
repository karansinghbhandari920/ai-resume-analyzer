from datetime import datetime

import streamlit as st

import auth
import database
from parser import extract_text, ResumeParser
from scorer import ATSScorer
from skills import SUPPORTED_ROLES
from utils import require_auth, page_header, render_gauge, clean_filename

require_auth()
user = auth.get_current_user()

page_header("STEP 1", "Upload Resume", "PDF, DOCX, or TXT - we'll extract, parse, and score it automatically.")

role = st.selectbox(
    "Target role (used for skill matching and scoring)",
    SUPPORTED_ROLES,
    index=SUPPORTED_ROLES.index(st.session_state.get("selected_role", SUPPORTED_ROLES[0]))
    if st.session_state.get("selected_role") in SUPPORTED_ROLES else 0,
)

uploaded_file = st.file_uploader("Drop your resume here", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    st.session_state["selected_role"] = role

    with st.spinner("Extracting and analyzing your resume..."):
        try:
            raw_text = extract_text(uploaded_file)
        except Exception as exc:
            st.error(f"Couldn't read that file: {exc}")
            st.stop()

        if not raw_text.strip():
            st.error("No extractable text was found in this file. If it's a scanned/image PDF, try a text-based export instead.")
            st.stop()

        parsed = ResumeParser(raw_text).parse()
        result = ATSScorer(raw_text, parsed, role=role).calculate()

        analysis_id = None
        try:
            analysis_id = database.save_resume_analysis(
                user_id=user["id"],
                access_token=user["access_token"],
                resume_name=clean_filename(uploaded_file.name),
                role=role,
                raw_text=raw_text,
                parsed_data=parsed.to_dict(),
                ats_score=result.overall_score,
                score_breakdown=result.breakdown,
            )
        except Exception as exc:
            st.warning(f"Analysis completed but couldn't be saved to your history: {exc}")

        st.session_state["current_analysis"] = {
            "id": analysis_id,
            "resume_name": clean_filename(uploaded_file.name),
            "role": role,
            "raw_text": raw_text,
            "parsed_data": parsed.to_dict(),
            "ats_score": result.overall_score,
            "score_breakdown": result.breakdown,
            "ai_review": None,
            "created_at": datetime.utcnow().isoformat(),
            "tips": result.tips,
        }
        st.session_state["current_analysis_id"] = analysis_id

    st.success("Resume analyzed.")

    info_col, preview_col = st.columns([1, 1.4], gap="large")
    with info_col:
        st.markdown('<div class="scan-card">', unsafe_allow_html=True)
        st.markdown(f"**File name:** {uploaded_file.name}")
        st.markdown(f"**Uploaded:** {datetime.utcnow().strftime('%b %d, %Y %H:%M UTC')}")
        st.markdown(f"**Target role:** {role}")
        st.write("")
        render_gauge(result.overall_score, label="ATS SCORE")
        st.markdown("</div>", unsafe_allow_html=True)

        nav1, nav2 = st.columns(2)
        if nav1.button("View Full ATS Breakdown →", use_container_width=True):
            st.switch_page("views/ats_analysis.py")
        if nav2.button("Get AI Review →", use_container_width=True):
            st.switch_page("views/ai_review.py")

    with preview_col:
        st.markdown('<div class="eyebrow">RESUME PREVIEW</div>', unsafe_allow_html=True)
        st.text_area("Extracted text", raw_text, height=420, label_visibility="collapsed")
else:
    st.info("Upload a resume to get started. We support PDF, DOCX, and TXT files up to 10MB.")
