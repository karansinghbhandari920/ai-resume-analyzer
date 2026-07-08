"""
utils.py
Shared helpers used across every page: theming, session-state bootstrap,
and small HTML component builders for the "scan readout" design system.
Keeping these here avoids duplicating markup logic in every page module.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

ASSETS_DIR = Path(__file__).parent / "assets"


# --------------------------------------------------------------------------- #
# Theming
# --------------------------------------------------------------------------- #
def load_css() -> None:
    """Inject the shared stylesheet. Safe to call on every page."""
    css_path = ASSETS_DIR / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def page_header(eyebrow: str, title: str, subtitle: str | None = None) -> None:
    st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.markdown(f'<h1 class="app-title">{title}</h1>', unsafe_allow_html=True)
    if subtitle:
        st.caption(subtitle)


# --------------------------------------------------------------------------- #
# Session state
# --------------------------------------------------------------------------- #
def init_session_state() -> None:
    defaults = {
        "auth_user": None,          # dict: {id, email, access_token, refresh_token}
        "current_analysis": None,   # dict: most recently parsed/scored resume
        "current_analysis_id": None,
        "chat_messages": [],        # resume chatbot transcript for this session
        "selected_role": "Data Analyst",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def is_authenticated() -> bool:
    return st.session_state.get("auth_user") is not None


def require_auth() -> None:
    """Call at the top of every page in pages/. Bounces back to app.py if
    there's no active session, since Streamlit pages run independently."""
    init_session_state()
    if not is_authenticated():
        st.warning("Please sign in to continue.")
        st.page_link("app.py", label="Go to Sign In", icon="🔐")
        st.stop()


# --------------------------------------------------------------------------- #
# Score → color banding (shared by gauges, chips, grades everywhere)
# --------------------------------------------------------------------------- #
def score_color(score: float) -> str:
    if score >= 75:
        return "#3DDC97"  # mint
    if score >= 50:
        return "#F2B84B"  # amber
    return "#E5616E"      # red


def score_grade(score: float) -> str:
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"


# --------------------------------------------------------------------------- #
# HTML component builders
# --------------------------------------------------------------------------- #
def render_gauge(score: float, label: str = "ATS SCORE", max_score: int = 100) -> None:
    """Renders the signature radial 'scan' gauge used for ATS score, role
    match %, and job-description match % throughout the app."""
    pct = max(0, min(100, (score / max_score) * 100))
    color = score_color(pct if max_score == 100 else score)
    html = f"""
    <div class="scan-gauge-wrap">
        <div class="scan-gauge" style="--pct:{pct}; --gauge-color:{color};">
            <div class="gauge-readout">
                <div class="gauge-score">{score:.0f}</div>
                <div class="gauge-of">/ {max_score}</div>
            </div>
        </div>
        <div>
            <div class="eyebrow" style="margin-bottom:.15rem;">{label}</div>
            <div class="grade-badge" style="color:{color}; border-color:{color};">
                Grade {score_grade(pct if max_score == 100 else score)}
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_metric_card(label: str, value: str, delta: str | None = None) -> None:
    delta_html = f'<div class="delta">{delta}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chips(items: list[str], kind: str = "default") -> None:
    """kind: 'match' (mint), 'missing' (amber), 'risk' (red), or 'default'."""
    css_class = {"match": "chip--match", "missing": "chip--missing", "risk": "chip--risk"}.get(kind, "")
    if not items:
        st.caption("None found.")
        return
    chips_html = "".join(f'<span class="chip {css_class}">{i}</span>' for i in items)
    st.markdown(f'<div class="chip-row">{chips_html}</div>', unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# Misc helpers
# --------------------------------------------------------------------------- #
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))


def truncate(text: str, max_chars: int = 6000) -> str:
    """Gemini calls are billed/limited by tokens — keep prompt payloads sane
    even if someone uploads an unusually long resume."""
    return text if len(text) <= max_chars else text[:max_chars] + "\n...[truncated]"


def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def load_analysis_into_session(row: dict) -> None:
    """Pulls a resume_analysis DB row into session state so other pages
    (ATS Analysis, AI Suggestions, Chatbot, ...) can pick it up."""
    st.session_state["current_analysis"] = row
    st.session_state["current_analysis_id"] = row.get("id")
    if row.get("role"):
        st.session_state["selected_role"] = row["role"]
