"""
AttritionIQ — FastAPI Main Application
=========================================
Application factory, middleware registration, router mounting,
startup/shutdown lifecycle, and global exception handlers.
"""

import time
import uuid
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.config import settings
from app.database import engine, create_tables
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

# Routers
from app.routes import (
    auth,
    employees,
    datasets,
    predictions,
    analytics,
    reports,
    model_registry,
    admin,
    health,
    notifications,
)

logger = structlog.get_logger(__name__)


# ============================================================
# Rate Limiter
# ============================================================
limiter = Limiter(key_func=get_remote_address)


# ============================================================
# Lifespan (Startup / Shutdown)
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    # Startup
    logger.info("Starting AttritionIQ Platform", version=settings.APP_VERSION, env=settings.APP_ENV)

    # Initialize Redis cache
    redis = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf8",
        decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis), prefix="attritioniq_cache")
    logger.info("Redis cache initialized")

    # In development, auto-create tables
    if settings.is_development:
        await create_tables()
        logger.info("Database tables verified")

    logger.info("AttritionIQ Platform started successfully")
    yield

    # Shutdown
    await engine.dispose()
    logger.info("AttritionIQ Platform shut down cleanly")


# ============================================================
# Application Factory
# ============================================================
def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="AttritionIQ — Employee Attrition Prediction Platform",
        description=(
            "Enterprise-grade HR Analytics platform powered by Explainable AI. "
            "Predicts employee attrition, explains predictions using SHAP, "
            "and provides actionable retention recommendations."
        ),
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
        swagger_ui_parameters={
            "deepLinking": True,
            "displayRequestDuration": True,
            "filter": True,
        },
    )

    # ========================
    # Rate Limiter
    # ========================
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # ========================
    # Middleware (order matters — outermost first)
    # ========================
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Page-Count"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(LoggingMiddleware)

    # ========================
    # Exception Handlers
    # ========================
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            errors.append({"field": field, "message": error["msg"], "type": error["type"]})
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"success": False, "message": "Validation error", "errors": errors},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        error_id = str(uuid.uuid4())[:8]
        logger.error(
            "Unhandled exception",
            error_id=error_id,
            path=request.url.path,
            method=request.method,
            error=str(exc),
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Internal server error. Please try again.",
                "error_id": error_id,
            },
        )

    # ========================
    # Request ID Middleware
    # ========================
    @app.middleware("http")
    async def add_request_id(request: Request, call_next: Any) -> Any:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        return response

    # ========================
    # Routers
    # ========================
    prefix = settings.API_PREFIX

    app.include_router(health.router, tags=["Health"])
    app.include_router(auth.router, prefix=f"{prefix}/auth", tags=["Authentication"])
    app.include_router(employees.router, prefix=f"{prefix}/employees", tags=["Employees"])
    app.include_router(datasets.router, prefix=f"{prefix}/datasets", tags=["Datasets"])
    app.include_router(predictions.router, prefix=f"{prefix}/predictions", tags=["Predictions"])
    app.include_router(analytics.router, prefix=f"{prefix}/analytics", tags=["Analytics"])
    app.include_router(reports.router, prefix=f"{prefix}/reports", tags=["Reports"])
    app.include_router(model_registry.router, prefix=f"{prefix}/models", tags=["Model Registry"])
    app.include_router(notifications.router, prefix=f"{prefix}/notifications", tags=["Notifications"])
    app.include_router(admin.router, prefix=f"{prefix}/admin", tags=["Admin"])

    return app


app = create_application()
