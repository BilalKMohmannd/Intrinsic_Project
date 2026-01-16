from __future__ import annotations

import streamlit as st

from lib.api_client import api_get
from lib.auth import is_admin, require_login, sidebar

st.set_page_config(page_title="Dashboard - SMS Manager", page_icon="🏠", layout="wide")

u = require_login()
sidebar()

st.title("🏠 Dashboard")
st.caption(f"Welcome back, {u.get('username')}!")

try:
    stats = api_get("/dashboard/stats")
except Exception as e:
    st.error(f"Failed to load dashboard stats: {e}")
    stats = {}

col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Numbers", stats.get("active_phone_numbers", 0))
col2.metric("Unread SMS", stats.get("unread_sms", 0))
col3.metric("SMS Today", stats.get("sms_today", 0))
col4.metric("Active Users", stats.get("active_users", 0) if is_admin() else "-")

st.divider()

st.subheader("Quick Links")
st.page_link("pages/1_Inbox.py", label="Go to Inbox", icon="📩")
if is_admin():
    st.page_link("pages/2_Numbers.py", label="Manage Phone Numbers", icon="📱")
    st.page_link("pages/3_Users.py", label="Manage Users", icon="👥")
