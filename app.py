"""
app.py
Entry point. Renders sign-in/sign-up when there's no session, and otherwise
builds the sidebar navigation with st.navigation/st.Page - which lets the
page list itself be conditional (no Admin Dashboard entry for non-admins,
no app pages at all before login) rather than relying on Streamlit's static
auto-discovered pages/ folder.
"""
from dotenv import load_dotenv
load_dotenv()

import streamlit as st

import auth
import database
from utils import load_css, init_session_state, is_authenticated

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)
load_css()
init_session_state()


# --------------------------------------------------------------------------- #
# Sign in / sign up (rendered as the page itself when logged out)
# --------------------------------------------------------------------------- #
def render_login() -> None:
    left, right = st.columns([1.1, 1], gap="large")

    with left:
        st.markdown('<div class="eyebrow">AI RESUME ANALYZER</div>', unsafe_allow_html=True)
        st.markdown(
            '<h1 class="app-title">Know exactly why a resume<br/>'
            '<span>passes — or doesn\'t.</span></h1>',
            unsafe_allow_html=True,
        )
        st.write(
            "Upload a resume to get an ATS score, role-fit analysis, AI-written "
            "feedback, tailored cover letters, and an interview prep kit — all "
            "in one place."
        )
        st.markdown(
            """
            <div class="chip-row">
                <span class="chip chip--match">ATS Scoring</span>
                <span class="chip chip--match">Role Matching</span>
                <span class="chip chip--missing">JD Gap Analysis</span>
                <span class="chip">AI Review</span>
                <span class="chip">Career Roadmap</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="scan-card">', unsafe_allow_html=True)
        tab_signin, tab_signup = st.tabs(["Sign In", "Create Account"])

        with tab_signin:
            with st.form("signin_form"):
                email = st.text_input("Email", key="signin_email")
                password = st.text_input("Password", type="password", key="signin_password")
                submitted = st.form_submit_button("Sign In", use_container_width=True)
            if submitted:
                if not email or not password:
                    st.error("Enter both email and password.")
                else:
                    with st.spinner("Signing in..."):
                        ok, message = auth.sign_in(email, password)
                    if ok:
                        _finish_login()
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

        with tab_signup:
            with st.form("signup_form"):
                full_name = st.text_input("Full name", key="signup_name")
                email = st.text_input("Email", key="signup_email")
                password = st.text_input("Password", type="password", key="signup_password",
                                          help="At least 6 characters.")
                submitted = st.form_submit_button("Create Account", use_container_width=True)
            if submitted:
                if not email or not password:
                    st.error("Enter both email and password.")
                else:
                    with st.spinner("Creating your account..."):
                        ok, message = auth.sign_up(email, password, full_name)
                    if ok:
                        if is_authenticated():
                            _finish_login()
                            st.rerun()
                        st.success(message)
                    else:
                        st.error(message)
        st.markdown("</div>", unsafe_allow_html=True)


def _finish_login() -> None:
    """After a successful sign-in/sign-up, look up admin status once so the
    nav menu can conditionally show the Admin Dashboard."""
    user = auth.get_current_user()
    if user:
        try:
            is_admin_flag = database.check_is_admin(user["id"], user["access_token"])
            st.session_state["auth_user"]["is_admin"] = is_admin_flag
        except Exception:
            pass  # Supabase not configured yet - app still usable, just no admin gating


# --------------------------------------------------------------------------- #
# Sidebar branding (rendered above the nav widget)
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown('<div class="app-title">🧠 Resume<span>AI</span></div>', unsafe_allow_html=True)
    st.caption("AI-powered resume intelligence")
    st.divider()

# --------------------------------------------------------------------------- #
# Build navigation
# --------------------------------------------------------------------------- #
login_page = st.Page(render_login, title="Sign In", icon="🔐", default=not is_authenticated())

if is_authenticated():
    dashboard = st.Page("views/dashboard.py", title="Dashboard", icon="📊", default=True)
    upload = st.Page("views/upload_resume.py", title="Upload Resume", icon="📤")
    ats = st.Page("views/ats_analysis.py", title="ATS Analysis", icon="🎯")
    job_match = st.Page("views/job_match.py", title="Job Match", icon="🔍")
    ai_suggestions = st.Page("views/ai_suggestions.py", title="AI Suggestions", icon="✨")
    ai_review = st.Page("views/ai_review.py", title="AI Review", icon="📝")
    cover_letter = st.Page("views/cover_letter.py", title="Cover Letter", icon="✉️")
    interview_prep = st.Page("views/interview_questions.py", title="Interview Prep", icon="🎤")
    chatbot = st.Page("views/chatbot.py", title="Resume Chatbot", icon="💬")
    roadmap = st.Page("views/roadmap.py", title="Career Roadmap", icon="🗺️")
    analytics_page = st.Page("views/analytics_page.py", title="Analytics", icon="📈")
    profile = st.Page("views/profile.py", title="Profile", icon="👤")
    settings_page = st.Page("views/settings_page.py", title="Settings", icon="⚙️")

    pages = {
        "Workspace": [dashboard, upload, ats, job_match],
        "AI Tools": [ai_suggestions, ai_review, cover_letter, interview_prep, chatbot, roadmap],
        "Account": [analytics_page, profile, settings_page],
    }
    if auth.is_admin():
        admin_page = st.Page("views/admin.py", title="Admin Dashboard", icon="🛡️")
        pages["Admin"] = [admin_page]

    nav = st.navigation(pages)
else:
    nav = st.navigation([login_page])

nav.run()

# --------------------------------------------------------------------------- #
# Sidebar footer: current user + sign out (rendered after nav so it sits
# below the page list)
# --------------------------------------------------------------------------- #
if is_authenticated():
    with st.sidebar:
        st.divider()
        user = auth.get_current_user()
        st.caption(f"Signed in as **{user['email']}**")
        if st.button("Sign Out", use_container_width=True):
            auth.sign_out()
            st.rerun()
