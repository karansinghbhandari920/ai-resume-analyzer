"""
analytics.py
Turns raw Supabase rows into pandas DataFrames ready for Plotly, for both
the per-user Analytics page and the Admin Dashboard.
"""
from __future__ import annotations

import pandas as pd

import database


def build_user_analytics(user_id: str, access_token: str) -> dict:
    summary = database.get_user_analytics_summary(user_id, access_token)

    history_df = pd.DataFrame(summary["history"])
    if not history_df.empty:
        history_df["date"] = pd.to_datetime(history_df["date"])
        history_df = history_df.sort_values("date")

    role_df = pd.DataFrame(
        [{"role": role, "count": count} for role, count in summary["role_counts"].items()]
    ).sort_values("count", ascending=False) if summary["role_counts"] else pd.DataFrame(columns=["role", "count"])

    return {
        "total": summary["total"],
        "avg_score": summary["avg_score"],
        "best_score": summary["best_score"],
        "history_df": history_df,
        "role_df": role_df,
    }


def build_admin_analytics() -> dict:
    stats = database.get_admin_stats()
    role_popularity = pd.DataFrame(database.get_admin_role_popularity())
    daily_activity = pd.DataFrame(database.get_admin_daily_activity())

    if not daily_activity.empty:
        daily_activity["day"] = pd.to_datetime(daily_activity["day"])
        daily_activity = daily_activity.sort_values("day")

    return {
        "total_users": stats.get("total_users", 0),
        "total_analyses": stats.get("total_analyses", 0),
        "avg_score": stats.get("avg_score", 0),
        "best_score": stats.get("best_score", 0),
        "analyses_today": stats.get("analyses_today", 0),
        "role_popularity_df": role_popularity,
        "daily_activity_df": daily_activity,
    }
