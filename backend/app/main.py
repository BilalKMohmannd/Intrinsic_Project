from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

from app.bootstrap import bootstrap_admin
from app.database import Base, engine
from app.routers import auth, dashboard, logs, messages, numbers, users, webhook

app = FastAPI(title="Multi-Number SMS Manager", version="0.1.0")


@app.on_event("startup")
def _startup() -> None:
    Base.metadata.create_all(bind=engine)
    bootstrap_admin()


app.include_router(auth.router)
app.include_router(numbers.router)
app.include_router(messages.router)
app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(logs.router)
app.include_router(webhook.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
