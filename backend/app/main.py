from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.query import router as query_router
from app.api.routes.auth import router as auth_router
from app.api.routes.documents import router as documents_router
from app.core.settings import settings


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
    allow_origins=["*"],  # For dev. In production, change to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Routes
# ============================================================

app.include_router(
    query_router,
)
app.include_router(
    auth_router,
)
app.include_router(
    documents_router,
)


# ============================================================
# Root
# ============================================================


@app.get("/")
async def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "Running",
    }


# ============================================================
# Health Check
# ============================================================


@app.get("/health")
async def health():
    return {
        "status": "Healthy",
    }