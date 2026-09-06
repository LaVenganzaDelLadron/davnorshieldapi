from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.config import settings
from app.database.init_db import init_database
from app.workers.scheduler import scheduler, shutdown_scheduler, start_scheduler

openapi_tags = [
    {"name": "Authentication", "description": "Register, log in, and manage sessions."},
    {"name": "Users", "description": "Administrative user management."},
    {"name": "Scam Reports", "description": "Citizen-submitted scam reports."},
    {"name": "Scanner", "description": "Threat scanning endpoints."},
    {"name": "Alerts", "description": "Broadcast and locality alerts."},
    {"name": "Cyber Weather", "description": "Daily cyber risk forecasting."},
    {"name": "Heatmap", "description": "Geospatial statistics for the frontend map."},
    {"name": "Barangays", "description": "Barangay reference data."},
    {"name": "Municipalities", "description": "Municipality reference data and summaries."},
    {"name": "Dashboard", "description": "LGU dashboards and analytics."},
    {"name": "Schools", "description": "School awareness and phishing statistics."},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and shut down application infrastructure."""

    await init_database()
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(
    title="DavnorShield API",
    version="1.0.0",
    description="AI-powered community cyber threat intelligence platform for Davao del Norte.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=openapi_tags,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    # This API is intentionally consumable by clients hosted on any domain.
    # A regex is used instead of ``[\"*\"]`` so credentialed browser requests
    # receive the calling origin in ``Access-Control-Allow-Origin``.
    allow_origins=[],
    allow_origin_regex=r".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
async def root() -> dict[str, str]:
    """Return a simple API status payload."""

    return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "status": "ok"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Return application health status."""

    return {"status": "healthy"}
