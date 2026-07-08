"""
database.py
All Supabase Postgres reads/writes live here. Two client strategies are used:

1. A per-request client authenticated with the *user's* access token, so
   Row Level Security policies (see sql/schema.sql) scope every query to
   that user automatically. We deliberately do NOT reuse a single cached
   client for this, because st.cache_resource is shared across every
   session in the same server process - caching a user-authenticated
   client would leak one user's session into another's requests.

2. A cached service-role client, used only by the Admin Dashboard to read
   aggregate views across all users. This key must never reach the browser.
"""
from __future__ import annotations

import os
from typing import Any

import streamlit as st
from supabase import create_client, Client


# --------------------------------------------------------------------------- #
# Client factories
# --------------------------------------------------------------------------- #
def _user_client(access_token: str) -> Client:
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_ANON_KEY", "")
    client = create_client(url, key)
    client.postgrest.auth(access_token)
    return client


@st.cache_resource(show_spinner=False)
def _admin_client() -> Client:
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not key:
        raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY is not set - required for the Admin Dashboard.")
    return create_client(url, key)


# --------------------------------------------------------------------------- #
# Resume analyses
# --------------------------------------------------------------------------- #
def save_resume_analysis(
    user_id: str,
    access_token: str,
    resume_name: str,
    role: str | None,
    raw_text: str,
    parsed_data: dict,
    ats_score: float,
    score_breakdown: dict,
    ai_review: dict | None = None,
) -> str | None:
    client = _user_client(access_token)
    payload = {
        "user_id": user_id,
        "resume_name": resume_name,
        "role": role,
        "raw_text": raw_text,
        "parsed_data": parsed_data,
        "ats_score": ats_score,
        "score_breakdown": score_breakdown,
        "ai_review": ai_review,
    }
    res = client.table("resume_analysis").insert(payload).execute()
    if res.data:
        return res.data[0]["id"]
    return None


def update_analysis_ai_review(analysis_id: str, access_token: str, ai_review: dict) -> None:
    client = _user_client(access_token)
    client.table("resume_analysis").update({"ai_review": ai_review}).eq("id", analysis_id).execute()


def get_user_analyses(user_id: str, access_token: str, limit: int = 50) -> list[dict]:
    client = _user_client(access_token)
    res = (
        client.table("resume_analysis")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data or []


def get_analysis_by_id(analysis_id: str, access_token: str) -> dict | None:
    client = _user_client(access_token)
    res = client.table("resume_analysis").select("*").eq("id", analysis_id).single().execute()
    return res.data


# --------------------------------------------------------------------------- #
# Job description matches
# --------------------------------------------------------------------------- #
def save_job_match(
    user_id: str,
    access_token: str,
    analysis_id: str | None,
    job_title: str,
    job_description: str,
    match_score: float,
    matching_skills: list[str],
    missing_keywords: list[str],
) -> str | None:
    client = _user_client(access_token)
    payload = {
        "user_id": user_id,
        "analysis_id": analysis_id,
        "job_title": job_title,
        "job_description": job_description,
        "match_score": match_score,
        "matching_skills": matching_skills,
        "missing_keywords": missing_keywords,
    }
    res = client.table("job_matches").insert(payload).execute()
    return res.data[0]["id"] if res.data else None


def get_user_job_matches(user_id: str, access_token: str, limit: int = 50) -> list[dict]:
    client = _user_client(access_token)
    res = (
        client.table("job_matches")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data or []


# --------------------------------------------------------------------------- #
# Resume chatbot history
# --------------------------------------------------------------------------- #
def save_chat_message(user_id: str, access_token: str, analysis_id: str | None, role: str, message: str) -> None:
    client = _user_client(access_token)
    client.table("chat_history").insert(
        {"user_id": user_id, "analysis_id": analysis_id, "role": role, "message": message}
    ).execute()


def get_chat_history(user_id: str, access_token: str, analysis_id: str | None, limit: int = 50) -> list[dict]:
    client = _user_client(access_token)
    query = client.table("chat_history").select("*").eq("user_id", user_id)
    if analysis_id:
        query = query.eq("analysis_id", analysis_id)
    res = query.order("created_at", desc=False).limit(limit).execute()
    return res.data or []


# --------------------------------------------------------------------------- #
# Per-user analytics
# --------------------------------------------------------------------------- #
def get_user_analytics_summary(user_id: str, access_token: str) -> dict[str, Any]:
    analyses = get_user_analyses(user_id, access_token, limit=500)
    if not analyses:
        return {"total": 0, "avg_score": 0, "best_score": 0, "history": [], "role_counts": {}}

    scores = [a["ats_score"] for a in analyses if a.get("ats_score") is not None]
    role_counts: dict[str, int] = {}
    for a in analyses:
        role = a.get("role") or "Unspecified"
        role_counts[role] = role_counts.get(role, 0) + 1

    return {
        "total": len(analyses),
        "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "best_score": max(scores) if scores else 0,
        "history": [
            {"date": a["created_at"], "score": a["ats_score"], "resume_name": a["resume_name"]}
            for a in reversed(analyses)
        ],
        "role_counts": role_counts,
    }


def get_profile(user_id: str, access_token: str) -> dict | None:
    client = _user_client(access_token)
    res = client.table("profiles").select("*").eq("id", user_id).single().execute()
    return res.data


def update_profile(user_id: str, access_token: str, full_name: str) -> None:
    client = _user_client(access_token)
    client.table("profiles").update({"full_name": full_name}).eq("id", user_id).execute()


# --------------------------------------------------------------------------- #
# Admin
# --------------------------------------------------------------------------- #
def check_is_admin(user_id: str, access_token: str) -> bool:
    try:
        client = _user_client(access_token)
        res = client.table("profiles").select("is_admin").eq("id", user_id).single().execute()
        return bool(res.data and res.data.get("is_admin"))
    except Exception:
        return False


def get_admin_stats() -> dict[str, Any]:
    client = _admin_client()
    res = client.table("admin_stats").select("*").single().execute()
    return res.data or {}


def get_admin_role_popularity() -> list[dict]:
    client = _admin_client()
    res = client.table("admin_role_popularity").select("*").execute()
    return res.data or []


def get_admin_daily_activity() -> list[dict]:
    client = _admin_client()
    res = client.table("admin_daily_activity").select("*").execute()
    return res.data or []
