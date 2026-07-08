import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

import auth
import analytics
from utils import require_auth, page_header, render_metric_card

require_auth()

if not auth.is_admin():
    st.error("This page is restricted to administrators.")
    st.stop()

page_header("ADMIN", "Admin Dashboard", "Platform-wide usage and quality metrics.")

try:
    data = analytics.build_admin_analytics()
except Exception as exc:
    st.error(
        f"Couldn't load admin stats: {exc}\n\n"
        "Make sure SUPABASE_SERVICE_ROLE_KEY is set and the admin_stats / "
        "admin_role_popularity / admin_daily_activity views exist (see sql/schema.sql)."
    )
    st.stop()

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    render_metric_card("Total Users", str(data["total_users"]))
with c2:
    render_metric_card("Total Analyses", str(data["total_analyses"]))
with c3:
    render_metric_card("Avg Score", f"{data['avg_score'] or 0:.0f}")
with c4:
    render_metric_card("Best Score", f"{data['best_score'] or 0:.0f}")
with c5:
    render_metric_card("Analyses Today", str(data["analyses_today"]))

st.write("")
col_left, col_right = st.columns([1.4, 1], gap="large")

with col_left:
    st.markdown('<div class="eyebrow">DAILY ACTIVITY</div>', unsafe_allow_html=True)
    if data["daily_activity_df"].empty:
        st.caption("No activity yet.")
    else:
        fig = go.Figure(go.Bar(
            x=data["daily_activity_df"]["day"], y=data["daily_activity_df"]["analyses"],
            marker_color="#3DDC97",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E8EDF2"), margin=dict(l=10, r=10, t=10, b=10),
            yaxis=dict(gridcolor="#2A3441"), height=320,
        )
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown('<div class="eyebrow">MOST POPULAR ROLES</div>', unsafe_allow_html=True)
    if data["role_popularity_df"].empty:
        st.caption("No role data yet.")
    else:
        fig_pie = px.pie(
            data["role_popularity_df"], names="role", values="analysis_count", hole=0.55,
            color_discrete_sequence=["#3DDC97", "#F2B84B", "#7AA7FF", "#E5616E", "#9D7CF2"],
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#E8EDF2"),
            margin=dict(l=10, r=10, t=10, b=10), height=320,
        )
        st.plotly_chart(fig_pie, use_container_width=True)
