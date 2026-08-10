from fastapi import FastAPI

from app.api.routes.query import router as query_router
from app.core.settings import settings
from app.voice.websocket import router as voice_ws_router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI Powered Government Scheme Discovery "
        "and Eligibility Platform"
    ),
)


# ============================================================
# Routes
# ============================================================

# Existing text/query API
app.include_router(query_router)

# New streaming voice WebSocket
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
# Health Check
# ============================================================


@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "Healthy",
    }