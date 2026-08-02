"""
AttritionIQ — Health Check Route
===================================
Returns system health status: DB, Redis, ML service, Celery.
"""

from datetime import datetime, timezone

import httpx
import structlog
from fastapi import APIRouter
from redis import asyncio as aioredis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Comprehensive health check endpoint.
    Returns connectivity status for all services.
    """
    health = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {},
    }
    overall_healthy = True

    # ========================
    # Database Check
    # ========================
    try:
        async_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://").replace("postgres://", "postgresql+asyncpg://")
        engine = create_async_engine(async_url, pool_pre_ping=True)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        health["services"]["database"] = {"status": "connected", "type": "postgresql"}
    except Exception as e:
        health["services"]["database"] = {"status": "disconnected", "error": str(e)}
        overall_healthy = False

    # ========================
    # Redis Check
    # ========================
    try:
        redis = aioredis.from_url(settings.REDIS_URL, socket_timeout=2)
        await redis.ping()
        await redis.aclose()
        health["services"]["redis"] = {"status": "connected"}
    except Exception as e:
        health["services"]["redis"] = {"status": "disconnected", "error": str(e)}
        overall_healthy = False

    # ========================
    # ML Service Check
    # ========================
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{settings.ML_SERVICE_URL}/health")
            if response.status_code == 200:
                health["services"]["ml_service"] = {"status": "connected"}
            else:
                health["services"]["ml_service"] = {"status": "degraded", "http_status": response.status_code}
                overall_healthy = False
    except Exception as e:
        health["services"]["ml_service"] = {"status": "disconnected", "error": str(e)}
        overall_healthy = False

    # ========================
    # Celery Check (via Redis)
    # ========================
    try:
        redis = aioredis.from_url(settings.CELERY_BROKER_URL, socket_timeout=2)
        await redis.ping()
        await redis.aclose()
        health["services"]["celery"] = {"status": "broker_connected"}
    except Exception as e:
        health["services"]["celery"] = {"status": "broker_disconnected", "error": str(e)}
        overall_healthy = False

    if not overall_healthy:
        health["status"] = "degraded"

    return health


@router.get("/", tags=["Health"])
async def root() -> dict:
    """Root endpoint — API info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
