from fastapi import FastAPI

from app.api.routes.query import router as query_router
from app.core.settings import settings


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

app.include_router(
    query_router,
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