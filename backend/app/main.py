"""FastAPI Application Main Entry Point."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from backend.app.core.config import settings
from backend.app.core.database import create_tables
from backend.app.routes import (
    health, auth, products, plans, subscriptions, invoices, payments,
    dashboard, discounts, quotation_templates,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Create all tables on startup (idempotent)."""
    logger.info("Creating database tables...")
    create_tables()
    logger.info("Tables ready.")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Odoo x FLUX Lucknow Hackathon 2026 — Subscription Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Exception Handlers ────────────────────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Formats Pydantic validation errors into friendly field-level messages."""
    errors = []
    for err in exc.errors():
        field = " -> ".join([str(loc) for loc in err.get("loc", []) if loc != "body"])
        message = err.get("msg", "Invalid input")
        errors.append(f"{field}: {message}" if field else message)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "data": None,
            "error": "Validation Error",
            "message": "; ".join(errors),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global catch-all — logs with request ID, never exposes stack traces."""
    logger.error("Unhandled exception on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "data": None,
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again.",
        },
    )


# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(plans.router, prefix="/api")
app.include_router(subscriptions.router, prefix="/api")
app.include_router(invoices.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(discounts.router, prefix="/api")
app.include_router(quotation_templates.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/")
def root():
    """Root status endpoint."""
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "docs": "/docs",
        "api": "/api/health",
    }
