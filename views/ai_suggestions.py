import streamlit as st

import auth
from ai_engine import AIEngineError
from parser import ParsedResume
from resume_rewriter import get_rewrite_candidates, rewrite_single, rewrite_batch
from utils import require_auth, page_header

require_auth()
user = auth.get_current_user()

page_header("AI TOOLS", "AI Bullet Rewriter", "Turn flat resume bullets into impact statements.")

analysis = st.session_state.get("current_analysis")
role = analysis.get("role") if analysis else st.session_state.get("selected_role")

tab_resume, tab_custom = st.tabs(["Rewrite from my resume", "Rewrite a custom bullet"])

with tab_resume:
    if not analysis:
        st.info("Upload and analyze a resume first to get suggestions pulled from it.")
        if st.button("Upload a Resume →", key="upload_from_suggestions"):
            st.switch_page("views/upload_resume.py")
    else:
        parsed_dict = analysis.get("parsed_data", {}) or {}
        parsed = ParsedResume(**{k: parsed_dict.get(k) for k in ParsedResume.__dataclass_fields__})
        candidates = get_rewrite_candidates(parsed, max_items=6)

        if not candidates:
            st.success("We didn't find any obviously weak bullet points - nice work!")
        else:
            st.caption(f"Found {len(candidates)} bullet points worth strengthening.")
            if st.button("Rewrite These With AI", type="primary"):
                with st.spinner("Rewriting..."):
                    try:
                        results = rewrite_batch(candidates, role=role)
                        st.session_state["rewrite_results"] = results
                    except AIEngineError as exc:
                        st.error(str(exc))

            for item in st.session_state.get("rewrite_results", []):
                st.markdown('<div class="scan-card">', unsafe_allow_html=True)
                st.markdown(f'<span class="chip chip--risk">BEFORE</span>', unsafe_allow_html=True)
                st.write(item["original"])
                if item.get("error"):
                    st.error(item["error"])
                else:
                    st.markdown(f'<span class="chip chip--match">AFTER</span>', unsafe_allow_html=True)
                    st.write(item["rewritten"])
                st.markdown("</div>", unsafe_allow_html=True)
                st.write("")

with tab_custom:
    bullet = st.text_area("Paste a bullet point", placeholder="Worked on dashboard project", height=100)
    target_role = st.text_input("Target role (optional)", value=role or "")
    if st.button("Rewrite Bullet", type="primary"):
        if not bullet.strip():
            st.error("Paste a bullet point first.")
        else:
            with st.spinner("Rewriting..."):
                result = rewrite_single(bullet, role=target_role or None)
            if result.get("error"):
                st.error(result["error"])
            else:
                st.markdown('<div class="scan-card">', unsafe_allow_html=True)
                st.markdown('<span class="chip chip--match">REWRITTEN</span>', unsafe_allow_html=True)
                st.write(result["rewritten"])
                st.markdown("</div>", unsafe_allow_html=True)
