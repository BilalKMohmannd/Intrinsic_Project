from __future__ import annotations

import pandas as pd
import streamlit as st

from lib.api_client import api_get, api_post
from lib.auth import require_login, sidebar

st.set_page_config(page_title="Manage Users - SMS Manager", page_icon="👥", layout="wide")

require_login()
sidebar()

st.title("👥 Manage Users")
st.caption("Create new user accounts and view existing ones.")

with st.expander("➕ Create a New User", expanded=False):
    with st.form("new_user_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", options=["user", "admin"], index=0)
        submitted = st.form_submit_button("Create User", type="primary")

        if submitted:
            if not username or not password:
                st.error("Username and password are required.")
            else:
                try:
                    api_post(
                        "/users",
                        json={"username": username, "password": password, "role": role},
                    )
                    st.success(f"User '{username}' created successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to create user: {e}")

st.divider()

st.subheader("Existing Users")

try:
    users = api_get("/users")
    if not users:
        st.info("No users found.")
    else:
        df = pd.DataFrame(users)
        st.dataframe(df[["id", "username", "role", "is_active"]], use_container_width=True, hide_index=True)
except Exception as e:
    st.error(f"Failed to load users: {e}")
