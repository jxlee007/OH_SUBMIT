"""FastAPI Application Main Entry Point."""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from backend.app.core.config import settings
from backend.app.routes import health

app = FastAPI(
    title=settings.APP_NAME,
    description="Odoo x FLUX Lucknow Hackathon 2026 API Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Validation Error Handler (Layer 2 & Evaluator requirement: friendly feedback)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Formats validation errors into friendly, readable feedback."""
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
            "message": "; ".join(errors)
        }
    )

# Include API routes
app.include_router(health.router, prefix="/api")

@app.get("/")
def root():
    """Root endpoint for status verification."""
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "docs": "/docs",
        "api": "/api/health"
    }

