import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

import auth
import analytics
from utils import require_auth, page_header, render_metric_card

require_auth()
user = auth.get_current_user()

page_header("INSIGHTS", "Analytics", "Trends across every resume you've analyzed.")

data = analytics.build_user_analytics(user["id"], user["access_token"])

if data["total"] == 0:
    st.info("Analyze a resume to start seeing analytics here.")
    st.stop()

c1, c2, c3 = st.columns(3)
with c1:
    render_metric_card("Total Analyses", str(data["total"]))
with c2:
    render_metric_card("Average ATS Score", f"{data['avg_score']:.0f}")
with c3:
    render_metric_card("Best ATS Score", f"{data['best_score']:.0f}")

st.write("")
st.markdown('<div class="eyebrow">SCORE HISTORY</div>', unsafe_allow_html=True)
fig_line = go.Figure()
fig_line.add_trace(go.Scatter(
    x=data["history_df"]["date"], y=data["history_df"]["score"],
    mode="lines+markers", line=dict(color="#3DDC97", width=3), marker=dict(size=8),
    fill="tozeroy", fillcolor="rgba(61,220,151,0.08)",
))
fig_line.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E8EDF2"), margin=dict(l=10, r=10, t=10, b=10),
    yaxis=dict(range=[0, 100], gridcolor="#2A3441"), xaxis=dict(gridcolor="#2A3441"), height=300,
)
st.plotly_chart(fig_line, use_container_width=True)

col_bar, col_pie = st.columns(2, gap="large")
with col_bar:
    st.markdown('<div class="eyebrow">ROLE POPULARITY (BAR)</div>', unsafe_allow_html=True)
    if data["role_df"].empty:
        st.caption("No role data yet.")
    else:
        fig_bar = go.Figure(go.Bar(
            x=data["role_df"]["role"], y=data["role_df"]["count"], marker_color="#3DDC97",
        ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E8EDF2"), margin=dict(l=10, r=10, t=10, b=10),
            yaxis=dict(gridcolor="#2A3441"), height=300,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

with col_pie:
    st.markdown('<div class="eyebrow">ROLE POPULARITY (SHARE)</div>', unsafe_allow_html=True)
    if data["role_df"].empty:
        st.caption("No role data yet.")
    else:
        fig_pie = px.pie(
            data["role_df"], names="role", values="count", hole=0.55,
            color_discrete_sequence=["#3DDC97", "#F2B84B", "#7AA7FF", "#E5616E", "#9D7CF2"],
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#E8EDF2"),
            margin=dict(l=10, r=10, t=10, b=10), height=300,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

st.write("")
st.markdown('<div class="eyebrow">ALL ANALYSES</div>', unsafe_allow_html=True)
table_df = data["history_df"][["date", "resume_name", "score"]].rename(
    columns={"date": "Date", "resume_name": "Resume", "score": "ATS Score"}
).iloc[::-1]
st.dataframe(table_df, use_container_width=True, hide_index=True)
