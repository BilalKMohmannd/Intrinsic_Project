from __future__ import annotations

import os

import httpx
import streamlit as st

API_BASE_URL = (os.getenv("API_BASE_URL") or "http://127.0.0.1:8000").strip().rstrip("/")

from lib.embedded_backend import ensure_backend_started

def _auth_headers() -> dict[str, str]:
    token = st.session_state.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}

def api_post(path: str, json_data: dict):
    ensure_backend_started(API_BASE_URL)
    with httpx.Client(timeout=20) as client:
        r = client.post(f"{API_BASE_URL}{path}", json=json_data, headers=_auth_headers())
        r.raise_for_status()
        return r.json()

def api_get(path: str, params: dict | None = None):
    ensure_backend_started(API_BASE_URL)
    with httpx.Client(timeout=20) as client:
        r = client.get(f"{API_BASE_URL}{path}", headers=_auth_headers(), params=params)
        r.raise_for_status()
        return r.json()

def api_patch(path: str, json_data: dict):
    ensure_backend_started(API_BASE_URL)
    with httpx.Client(timeout=20) as client:
        r = client.patch(f"{API_BASE_URL}{path}", headers=_auth_headers(), json=json_data)
        r.raise_for_status()
        return r.json()

def api_put(path: str, json_data: dict):
    ensure_backend_started(API_BASE_URL)
    with httpx.Client(timeout=20) as client:
        r = client.put(f"{API_BASE_URL}{path}", headers=_auth_headers(), json=json_data)
        r.raise_for_status()
        return r.json()
