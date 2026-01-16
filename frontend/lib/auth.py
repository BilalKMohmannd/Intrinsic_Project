from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from lib.api_client import API_BASE_URL, api_post


def _logo_path() -> Path | None:
    logo_candidates = [
        Path(__file__).resolve().parents[1] / "assets" / "intrinsic_tech_group_logo.jpeg",
        Path(__file__).resolve().parents[2] / "intrinsic_tech_group_logo.jpeg",
        Path.cwd() / "intrinsic_tech_group_logo.jpeg",
    ]
    return next((p for p in logo_candidates if p.exists()), None)

def login_screen() -> None:
    st.markdown(
        """
        <style>
          .login-wrap { max-width: 420px; margin: 0 auto; padding-top: 2.0rem; }
          .login-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 22px 20px; }
          .login-brand { text-align: center; font-weight: 800; font-size: 1.25rem; margin-top: 0.25rem; margin-bottom: 0.25rem; }
          .login-sub { text-align: center; opacity: 0.75; margin-bottom: 1rem; }
          .login-logo { display:flex; justify-content:center; margin-bottom: 0.25rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='login-wrap'><div class='login-card'>", unsafe_allow_html=True)

    logo_path = _logo_path()
    if logo_path:
        try:
            b64 = base64.b64encode(logo_path.read_bytes()).decode("ascii")
            st.markdown(
                f"<div class='login-logo'><img src='data:image/jpeg;base64,{b64}' style='width:120px; height:auto;' /></div>",
                unsafe_allow_html=True,
            )
        except Exception:
            pass

    st.markdown("<div class='login-brand'>IntrinsicAmerica</div>", unsafe_allow_html=True)
    st.markdown("<div class='login-sub'>Sign in to access your SMS dashboard</div>", unsafe_allow_html=True)

    with st.form("login"):
        username = st.text_input("Username", placeholder="admin")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)

    if submitted:
        try:
            resp = api_post("/auth/login", {"username": username, "password": password})
            st.session_state["access_token"] = resp["access_token"]
            st.session_state["user"] = resp["user"]
            st.rerun()
        except Exception:
            st.error("Login failed. Please check your credentials.")
            st.stop()

    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

def require_login() -> dict:
    if not st.session_state.get("access_token") or not st.session_state.get("user"):
        login_screen()
    return st.session_state["user"]

def is_admin() -> bool:
    u = st.session_state.get("user") or {}
    return str(u.get("role") or "").lower() == "admin"

def sidebar() -> None:
    with st.sidebar:
        st.page_link("Home.py", label="Dashboard", icon="🏠")
        st.page_link("pages/1_Inbox.py", label="Inbox", icon="📩")
        if is_admin():
            st.divider()
            st.caption("Admin")
            st.page_link("pages/2_Numbers.py", label="Manage Numbers", icon="📱")
            st.page_link("pages/3_Users.py", label="Manage Users", icon="👥")
            st.page_link("pages/4_Logs.py", label="Audit Logs", icon="📜")
        st.divider()
        u = st.session_state.get("user")
        if u:
            st.caption(f"Signed in as: {u.get('username')} ({u.get('role')})")
        if st.button("Sign out"):
            st.session_state.pop("access_token", None)
            st.session_state.pop("user", None)
            st.rerun()
