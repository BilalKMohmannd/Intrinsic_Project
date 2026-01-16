from __future__ import annotations

import pandas as pd
import streamlit as st

from lib.api_client import api_get
from lib.auth import require_login, sidebar

st.set_page_config(page_title="Audit Logs - SMS Manager", page_icon="📜", layout="wide")

require_login()
sidebar()

st.title("📜 Audit Logs")
st.caption("A record of all actions taken within the system.")

try:
    logs = api_get("/logs", params={"limit": 500})
    if not logs:
        st.info("No log entries found.")
    else:
        df = pd.DataFrame(logs)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        st.dataframe(df, use_container_width=True, hide_index=True)
except Exception as e:
    st.error(f"Failed to load audit logs: {e}")
