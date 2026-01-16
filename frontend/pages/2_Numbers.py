from __future__ import annotations

import pandas as pd
import streamlit as st

from lib.api_client import api_get, api_post, api_put
from lib.auth import require_login, sidebar

st.set_page_config(page_title="Manage Numbers - SMS Manager", page_icon="📱", layout="wide")

require_login()
sidebar()

st.title("📱 Manage Phone Numbers")
st.caption("Here you can add new Twilio numbers and assign them to users.")

try:
    numbers = api_get("/numbers")
    users = api_get("/users")
except Exception as e:
    st.error(f"Failed to load data: {e}")
    numbers = []
    users = []

with st.expander("➕ Add a New Phone Number", expanded=False):
    with st.form("new_number_form"):
        twilio_number = st.text_input("Twilio Number (E.164 format, e.g., +15551234567)")
        label = st.text_input("Label (e.g., 'Walmart US Store 01')")
        user_options = {u['id']: u['username'] for u in users}
        user_options[0] = "(Unassigned)"
        assigned_user_id = st.selectbox("Assign to User (Optional)", options=list(user_options.keys()), format_func=lambda x: user_options[x])
        submitted = st.form_submit_button("Add Number", type="primary")

        if submitted:
            try:
                api_post(
                    f"/numbers?twilio_number={twilio_number}",
                    json_data={
                        "label": label or None,
                        "assigned_user_id": int(assigned_user_id) if assigned_user_id else None,
                        "status": "active",
                    },
                )
                st.success(f"Successfully added {twilio_number}!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to add number: {e}")

st.divider()

st.subheader("Existing Numbers")

if not numbers:
    st.info("No numbers have been added yet.")
else:
    df = pd.DataFrame(numbers)
    df["assigned_user"] = df["assigned_user_id"].apply(lambda x: next((u['username'] for u in users if u['id'] == x), "-") if x else "-")
    st.dataframe(df[["twilio_number", "label", "status", "assigned_user"]], use_container_width=True, hide_index=True)

    st.subheader("Edit a Number")
    number_to_edit = st.selectbox("Select a number to edit", options=[n['id'] for n in numbers], format_func=lambda x: next((n['twilio_number'] for n in numbers if n['id'] == x), "-"))
    if number_to_edit:
        selected_num = next((n for n in numbers if n['id'] == number_to_edit), None)
        if selected_num:
            with st.form(f"edit_form_{number_to_edit}"):
                new_label = st.text_input("New Label", value=selected_num.get('label', ''))
                new_assigned_user_id = st.selectbox("Assign to User", options=list(user_options.keys()), format_func=lambda x: user_options[x], index=list(user_options.keys()).index(selected_num.get('assigned_user_id') or 0))
                update_submitted = st.form_submit_button("Update Number", type="primary")

                if update_submitted:
                    try:
                        api_put(
                            f"/numbers/{number_to_edit}",
                            json_data={
                                "label": new_label or None,
                                "assigned_user_id": int(new_assigned_user_id) if new_assigned_user_id else None,
                            },
                        )
                        st.success("Number updated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to update number: {e}")
