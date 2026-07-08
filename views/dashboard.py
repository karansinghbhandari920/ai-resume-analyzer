import streamlit as st
import plotly.graph_objects as go

import database
import auth
import analytics
from utils import (
    require_auth, page_header, render_gauge, render_metric_card,
    load_analysis_into_session, score_color,
)

require_auth()
user = auth.get_current_user()

page_header("OVERVIEW", "Dashboard", f"Welcome back, {user.get('full_name') or user['email']}.")

data = analytics.build_user_analytics(user["id"], user["access_token"])

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric_card("Total Analyses", str(data["total"]))
with col2:
    render_metric_card("Average ATS Score", f"{data['avg_score']:.0f}" if data["total"] else "—")
with col3:
    render_metric_card("Best ATS Score", f"{data['best_score']:.0f}" if data["total"] else "—")
with col4:
    top_role = data["role_df"].iloc[0]["role"] if not data["role_df"].empty else "—"
    render_metric_card("Most Analyzed Role", top_role)

st.write("")

left, right = st.columns([1.3, 1], gap="large")

with left:
    st.markdown('<div class="eyebrow">SCORE HISTORY</div>', unsafe_allow_html=True)
    if data["history_df"].empty:
        st.info("Upload a resume to start tracking your ATS score over time.")
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data["history_df"]["date"], y=data["history_df"]["score"],
            mode="lines+markers", line=dict(color="#3DDC97", width=3),
            marker=dict(size=7, color="#3DDC97"),
            hovertext=data["history_df"]["resume_name"],
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E8EDF2"), margin=dict(l=10, r=10, t=10, b=10),
            yaxis=dict(range=[0, 100], gridcolor="#2A3441"),
            xaxis=dict(gridcolor="#2A3441"), height=280,
        )
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown('<div class="eyebrow">CURRENT RESUME</div>', unsafe_allow_html=True)
    current = st.session_state.get("current_analysis")
    if current:
        st.markdown('<div class="scan-card">', unsafe_allow_html=True)
        render_gauge(current.get("ats_score", 0), label=current.get("resume_name", "RESUME"))
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("Open ATS Analysis →", use_container_width=True):
            st.switch_page("views/ats_analysis.py")
    else:
        st.markdown('<div class="scan-card">', unsafe_allow_html=True)
        st.write("No resume loaded yet.")
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("Upload a Resume →", use_container_width=True):
            st.switch_page("views/upload_resume.py")

st.write("")
st.markdown('<div class="eyebrow">RECENT ANALYSES</div>', unsafe_allow_html=True)

recent = data["history_df"]
if recent.empty:
    st.caption("Nothing here yet - your analyzed resumes will show up in this list.")
else:
    from database import get_user_analyses
    rows = get_user_analyses(user["id"], user["access_token"], limit=10)
    for row in rows:
        c1, c2, c3, c4 = st.columns([3, 2, 1.2, 1])
        c1.write(f"**{row['resume_name']}**")
        c2.write(row.get("role") or "—")
        score = row.get("ats_score") or 0
        c3.markdown(f'<span style="color:{score_color(score)}; font-family:monospace; font-weight:700;">{score:.0f}</span>', unsafe_allow_html=True)
        if c4.button("View", key=f"view_{row['id']}"):
            load_analysis_into_session(row)
            st.switch_page("views/ats_analysis.py")
