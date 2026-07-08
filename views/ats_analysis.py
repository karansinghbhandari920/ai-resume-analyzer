import streamlit as st
import plotly.graph_objects as go

import auth
from parser import ParsedResume
from scorer import generate_tips
from skills import SUPPORTED_ROLES, match_skills_to_role
from pdf_report import generate_pdf_report
from utils import require_auth, page_header, render_gauge, render_chips, score_color

require_auth()
user = auth.get_current_user()

page_header("STEP 2", "ATS Analysis", "Detailed breakdown of how your resume scores against ATS-style checks.")

analysis = st.session_state.get("current_analysis")
if not analysis:
    st.info("No resume loaded yet.")
    if st.button("Upload a Resume →"):
        st.switch_page("views/upload_resume.py")
    st.stop()

parsed_dict = analysis.get("parsed_data", {}) or {}
parsed = ParsedResume(**{k: parsed_dict.get(k) for k in ParsedResume.__dataclass_fields__})
# Defaults for any fields that came back None from storage
for list_field in ("skills", "education", "experience", "projects", "certifications", "sections_found", "bullet_points"):
    if getattr(parsed, list_field) is None:
        setattr(parsed, list_field, [])

breakdown = analysis.get("score_breakdown", {})
tips = analysis.get("tips") or generate_tips(breakdown, parsed)

top_left, top_right = st.columns([1, 1.6], gap="large")
with top_left:
    st.markdown('<div class="scan-card">', unsafe_allow_html=True)
    render_gauge(analysis.get("ats_score", 0), label=analysis.get("resume_name", "RESUME"))
    st.markdown("</div>", unsafe_allow_html=True)

    pdf_bytes = generate_pdf_report({**analysis, "tips": tips})
    st.download_button(
        "Download PDF Report", data=pdf_bytes,
        file_name=f"{analysis.get('resume_name', 'resume')}_report.pdf",
        mime="application/pdf", use_container_width=True,
    )

with top_right:
    st.markdown('<div class="eyebrow">SCORE BREAKDOWN</div>', unsafe_allow_html=True)
    if breakdown:
        labels = list(breakdown.keys())
        values = list(breakdown.values())
        colors = [score_color((v / {
            "Skills Match": 30, "Resume Sections": 15, "Contact Information": 10,
            "Action Verbs": 15, "Quantified Achievements": 15, "Readability": 10, "Word Count": 5,
        }.get(k, 100)) * 100) for k, v in zip(labels, values)]
        fig = go.Figure(go.Bar(x=values, y=labels, orientation="h", marker_color=colors))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E8EDF2"), margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(gridcolor="#2A3441"), height=280,
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()

contact_col, skills_col = st.columns(2, gap="large")
with contact_col:
    st.markdown('<div class="eyebrow">CONTACT INFORMATION</div>', unsafe_allow_html=True)
    st.write(f"**Name:** {parsed.name or '—'}")
    st.write(f"**Email:** {parsed.email or '—'}")
    st.write(f"**Phone:** {parsed.phone or '—'}")
    st.write(f"**LinkedIn:** {parsed.linkedin or '—'}")
    st.write(f"**GitHub:** {parsed.github or '—'}")

    st.markdown('<div class="eyebrow" style="margin-top:1rem;">SECTIONS DETECTED</div>', unsafe_allow_html=True)
    render_chips([s.title() for s in parsed.sections_found], kind="match")

with skills_col:
    st.markdown('<div class="eyebrow">DETECTED SKILLS</div>', unsafe_allow_html=True)
    render_chips(parsed.skills, kind="match")

st.divider()

st.markdown('<div class="eyebrow">ROLE MATCH</div>', unsafe_allow_html=True)
role = st.selectbox("Role", SUPPORTED_ROLES,
                     index=SUPPORTED_ROLES.index(analysis.get("role")) if analysis.get("role") in SUPPORTED_ROLES else 0)
match = match_skills_to_role(set(parsed.skills), role)

mcol1, mcol2 = st.columns([1, 2])
with mcol1:
    render_gauge(match["match_percent"], label=f"{role.upper()} MATCH")
with mcol2:
    st.write("**Strengths**")
    render_chips(match["strengths"], kind="match")
    st.write("**Missing Skills**")
    render_chips(match["missing_skills"], kind="missing")
    for rec in match["recommendations"]:
        st.caption(f"💡 {rec}")

st.divider()
st.markdown('<div class="eyebrow">SUGGESTIONS</div>', unsafe_allow_html=True)
for tip in tips:
    st.write(f"- {tip}")
