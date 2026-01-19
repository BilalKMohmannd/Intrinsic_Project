from __future__ import annotations

import re

import pandas as pd
import streamlit as st

from lib.api_client import api_get, api_patch, api_post
from lib.auth import require_login, sidebar

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

st.set_page_config(page_title="Inbox - SMS Manager", page_icon="📩", layout="wide")

require_login()
sidebar()

st.title("📩 Message Inbox")

st.session_state.setdefault("selected_number", None)
st.session_state.setdefault("selected_msg_id", None)


def _display_phone_only(v: str | None) -> str:
    if not v:
        return "-"
    m = re.findall(r"\+?\d+", str(v))
    if not m:
        return str(v)
    return "".join(m)

with st.sidebar:
    st.divider()
    if st_autorefresh:
        auto_refresh = st.checkbox("Auto-refresh", value=True)
        if auto_refresh:
            refresh_seconds = st.slider("Refresh interval (sec)", 5, 120, 5)
            st_autorefresh(interval=refresh_seconds * 1000, key="inbox_refresh")

top_left, top_right = st.columns([1, 1])
with top_left:
    if st.button("Refresh now", type="secondary"):
        st.rerun()
with top_right:
    st.caption("Updates automatically; use Refresh now if you just received an SMS.")

try:
    numbers = api_get("/numbers")
except Exception as e:
    st.error(f"Failed to load numbers: {e}")
    numbers = []

if not numbers:
    st.info("You have no phone numbers assigned to you.")
    st.stop()

selected_number = st.selectbox(
    "Select a phone number to view its inbox:",
    options=[n["twilio_number"] for n in numbers],
    format_func=lambda s: f"{s} ({next((n.get('label') for n in numbers if n['twilio_number'] == s), 'No label')})",
    key="selected_number",
)

st.divider()

if selected_number:
    try:
        msgs = api_get(f"/messages/{selected_number}", params={"limit": 100})
    except Exception as e:
        st.error(f"Failed to load messages: {e}")
        msgs = []

    if not msgs:
        st.info("No messages found for this number.")
        st.stop()

    left, right = st.columns([1, 2])

    with left:
        st.subheader("Messages")
        msg_ids = [m["id"] for m in msgs]
        selected_msg_id = st.radio(
            "Select a message to view",
            msg_ids,
            format_func=lambda mid: f"From: {_display_phone_only(next((m.get('from_number') for m in msgs if m['id'] == mid), '-'))} @ {pd.to_datetime(next(m.get('received_at') for m in msgs if m['id'] == mid)).strftime('%Y-%m-%d %H:%M')}",
            label_visibility="collapsed",
            key="selected_msg_id",
        )

    with right:
        st.subheader("Message Details")
        if selected_msg_id:
            msg = next((m for m in msgs if m["id"] == selected_msg_id), None)
            if msg:
                otp = msg.get("otp_code")
                otp_expired = bool(msg.get("otp_expired"))

                st.caption(f"Received at: {pd.to_datetime(msg.get('received_at')).strftime('%Y-%m-%d %H:%M:%S')} UTC")

                if otp and not otp_expired:
                    st.success("**OTP Code Detected**")
                    st.code(otp, language="text")
                    st.text_input("Copy OTP", value=otp, key=f"otp_copy_{msg['id']}")
                else:
                    st.warning("No active OTP code found.")

                st.text_area("Full Message Body", value=msg.get("message_body") or "", height=150, disabled=True)

                st.divider()
                st.subheader("Forward")
                with st.form(f"forward_{msg['id']}"):
                    forward_to = st.text_input("Forward to", placeholder="+15551234567")
                    forward_submitted = st.form_submit_button("Send", type="primary", use_container_width=True)

                if forward_submitted:
                    try:
                        resp = api_post(f"/messages/{msg['id']}/forward", {"to_number": forward_to})
                        sid = (resp or {}).get("provider_message_sid")
                        st.success(f"Forwarded{(' (sid: ' + sid + ')') if sid else ''}.")
                    except Exception as e:
                        st.error(f"Forward failed: {e}")

                c1, c2 = st.columns(2)
                is_read = bool(msg.get("is_read"))
                if not is_read:
                    if c1.button("Mark as Read", key=f"read_{msg['id']}"):
                        api_patch(f"/messages/{msg['id']}/read", {"is_read": True})
                        st.rerun()
                else:
                    if c2.button("Mark as Unread", key=f"unread_{msg['id']}"):
                        api_patch(f"/messages/{msg['id']}/read", {"is_read": False})
                        st.rerun()
