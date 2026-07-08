import streamlit as st

import auth
from ai_engine import generate_career_roadmap, AIEngineError
from parser import ParsedResume
from skills import SUPPORTED_ROLES
from utils import require_auth, page_header

require_auth()
user = auth.get_current_user()

page_header("AI TOOLS", "Career Roadmap", "A staged learning plan toward your target role.")

analysis = st.session_state.get("current_analysis")
current_skills = []
if analysis:
    parsed_dict = analysis.get("parsed_data", {}) or {}
    parsed = ParsedResume(**{k: parsed_dict.get(k) for k in ParsedResume.__dataclass_fields__})
    current_skills = parsed.skills or []

target_role = st.selectbox(
    "Target role", SUPPORTED_ROLES,
    index=SUPPORTED_ROLES.index(analysis.get("role")) if analysis and analysis.get("role") in SUPPORTED_ROLES else 0,
)

if not analysis:
    st.caption("Tip: upload a resume first so the roadmap can build on skills you already have.")

if st.button("Generate Roadmap", type="primary"):
    with st.spinner("Mapping out your path..."):
        try:
            roadmap = generate_career_roadmap(current_skills, target_role)
            st.session_state["career_roadmap"] = roadmap
        except AIEngineError as exc:
            st.error(str(exc))

roadmap = st.session_state.get("career_roadmap")
if roadmap:
    stages = [("beginner", "🌱 Beginner"), ("intermediate", "🚀 Intermediate"), ("advanced", "🏆 Advanced")]
    tabs = st.tabs([label for _, label in stages])
    for tab, (key, _) in zip(tabs, stages):
        with tab:
            stage = roadmap.get(key, {})
            st.markdown('<div class="eyebrow">SKILLS TO LEARN</div>', unsafe_allow_html=True)
            for s in stage.get("skills_to_learn", []):
                st.write(f"- {s}")
            st.markdown('<div class="eyebrow" style="margin-top:1rem;">CERTIFICATIONS</div>', unsafe_allow_html=True)
            for c in stage.get("certifications", []):
                st.write(f"- {c}")
            st.markdown('<div class="eyebrow" style="margin-top:1rem;">PROJECT IDEAS</div>', unsafe_allow_html=True)
            for p in stage.get("project_ideas", []):
                st.markdown(f'<div class="scan-card">{p}</div>', unsafe_allow_html=True)
                st.write("")
