from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
# CORS — allow Vite dev server and any localhost origin
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
# Health Check  (both /health and /api/health for the frontend)
# ============================================================


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
async def health():
    return {
        "status": "Healthy",
    }