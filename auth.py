"""
auth.py
Thin wrapper around Supabase Auth. Keeps the rest of the app from talking
to the supabase-py client directly so the auth strategy can change without
touching every page.

Session persistence note: Streamlit re-runs the whole script on every
interaction, so we keep the Supabase session (access/refresh tokens) inside
st.session_state. That persists across page navigation within one browser
tab/session but not across a hard refresh after the server restarts -
acceptable for a portfolio app; for a hardened production deploy you'd
additionally persist the refresh token in a signed cookie.
"""
from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()
import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()


@st.cache_resource(show_spinner=False)
def get_supabase_client() -> Client:
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_ANON_KEY", "")
    print("SUPABASE_URL =", os.environ.get("SUPABASE_URL"))
    print("SUPABASE_ANON_KEY =", os.environ.get("SUPABASE_ANON_KEY"))
    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL / SUPABASE_ANON_KEY are not set. Copy .env.example to "
            ".env and fill in your Supabase project credentials."
        )
    return create_client(url, key)


def sign_up(email: str, password: str, full_name: str = "") -> tuple[bool, str]:
    """Returns (success, message)."""
    try:
        client = get_supabase_client()
        result = client.auth.sign_up(
            {
                "email": email,
                "password": password,
                "options": {"data": {"full_name": full_name}},
            }
        )
        if result.user is None:
            return False, "Sign up failed. Please try again."
        if result.session is None:
            return True, "Account created! Check your inbox to confirm your email, then sign in."
        _store_session(result)
        return True, "Account created and signed in."
    except Exception as exc:  # noqa: BLE001 - surface a friendly message
        return False, _friendly_auth_error(exc)


def sign_in(email: str, password: str) -> tuple[bool, str]:
    try:
        client = get_supabase_client()
        result = client.auth.sign_in_with_password({"email": email, "password": password})
        if result.user is None or result.session is None:
            return False, "Invalid email or password."
        _store_session(result)
        return True, "Signed in."
    except Exception as exc:  # noqa: BLE001
        return False, _friendly_auth_error(exc)


def sign_out() -> None:
    try:
        client = get_supabase_client()
        client.auth.sign_out()
    except Exception:
        pass
    for key in ("auth_user", "current_analysis", "current_analysis_id", "chat_messages"):
        st.session_state.pop(key, None)


def get_current_user() -> dict | None:
    return st.session_state.get("auth_user")


def is_admin() -> bool:
    user = get_current_user()
    return bool(user and user.get("is_admin"))


def _store_session(result) -> None:
    user = result.user
    session = result.session
    full_name = ""
    if getattr(user, "user_metadata", None):
        full_name = user.user_metadata.get("full_name", "")
    st.session_state["auth_user"] = {
        "id": user.id,
        "email": user.email,
        "full_name": full_name,
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "is_admin": False,  # promoted by database.py:check_admin() after profile lookup
    }


def _friendly_auth_error(exc: Exception) -> str:
    msg = str(exc)
    if "User already registered" in msg:
        return "An account with that email already exists. Try signing in instead."
    if "Invalid login credentials" in msg:
        return "Invalid email or password."
    if "Password should be at least" in msg:
        return "Password is too short - use at least 6 characters."
    if "SUPABASE_URL" in msg or "SUPABASE_ANON_KEY" in msg:
        return str(exc)
    return f"Authentication error: {msg}"
