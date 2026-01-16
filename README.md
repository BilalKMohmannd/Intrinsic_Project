# Multi-Number SMS Management System (Twilio + Streamlit)

This is an MVP for managing multiple Twilio phone numbers and viewing inbound 2FA/OTP SMS messages in a centralized dashboard.

## Architecture

- FastAPI backend (API + Twilio webhook)
- Streamlit frontend (dashboard + inbox + admin tools)
- SQLite database (MVP)

## Setup

1) Create a virtualenv and install deps:

```bash
pip install -r requirements.txt
```

2) Create a `.env` file:

```bash
cp .env.example .env
```

3) Set **at minimum**:

- `ADMIN_PASSWORD` (bootstraps initial admin on first backend start)
- `JWT_SECRET` (secure random value)
- `TWILIO_AUTH_TOKEN` (required if signature enforcement is enabled)

## Run locally

Terminal 1 (backend):

```bash
./backend/run_backend.sh
```

Terminal 2 (frontend):

```bash
./frontend/run_frontend.sh
```

Open Streamlit:

- http://127.0.0.1:8501

## Twilio webhook

Configure each Twilio phone number's inbound Messaging webhook URL to:

- `https://YOUR_PUBLIC_DOMAIN/sms/webhook`

Twilio will send form-encoded fields including `To`, `From`, `Body`, `MessageSid`.

## Notes

- OTP extraction uses regex `\b\d{4,8}\b`.
- OTP visibility is automatically hidden after `OTP_VISIBILITY_MINUTES`.
- For production: switch `DATABASE_URL` to Postgres and deploy FastAPI + Streamlit as two services (Render/Railway/AWS).
