import streamlit as st

import auth
import database
from utils import require_auth, page_header

require_auth()
user = auth.get_current_user()

page_header("ACCOUNT", "Profile", "Your account details.")

profile = None
try:
    profile = database.get_profile(user["id"], user["access_token"])
except Exception:
    pass

st.markdown('<div class="scan-card">', unsafe_allow_html=True)
st.write(f"**Email:** {user['email']}")
if profile and profile.get("created_at"):
    st.write(f"**Member since:** {profile['created_at'][:10]}")
st.markdown("</div>", unsafe_allow_html=True)

st.write("")
st.markdown('<div class="eyebrow">DISPLAY NAME</div>', unsafe_allow_html=True)
with st.form("profile_form"):
    full_name = st.text_input("Full name", value=(profile or {}).get("full_name") or user.get("full_name") or "")
    submitted = st.form_submit_button("Save Changes")
if submitted:
    try:
        database.update_profile(user["id"], user["access_token"], full_name)
        st.session_state["auth_user"]["full_name"] = full_name
        st.success("Profile updated.")
    except Exception as exc:
        st.error(f"Couldn't update profile: {exc}")
