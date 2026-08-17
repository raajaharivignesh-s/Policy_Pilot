from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.query import router as query_router
from app.api.routes.auth import router as auth_router
from app.api.routes.documents import router as documents_router
from app.core.settings import settings
from app.voice.websocket import router as voice_ws_router
from app.database.base import Base
from app.database.connection import engine
import app.models  # noqa: F401

# Auto-initialize database tables (PostgreSQL or SQLite)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database schema init warning: {e}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI Powered Government Scheme Discovery "
        "and Eligibility Platform"
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Routes
# ============================================================

app.include_router(query_router)
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(voice_ws_router)


# ============================================================
# Root
# ============================================================


@app.get("/", tags=["Health"])
async def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "Running",
    }


# ============================================================
# Health Check  (both /health and /api/health for the frontend)
# ============================================================


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
async def health():
    return {
        "status": "Healthy",
    }