"""System and Database Health Check Router."""
from fastapi import APIRouter
from backend.app.core.database import check_db_connection
from backend.app.schemas.common import StandardResponse, HealthStatus

router = APIRouter(prefix="/health", tags=["System"])

@router.get("", response_model=StandardResponse[HealthStatus])
def get_health():
    """Returns application health and verifies live PostgreSQL connection."""
    db_status = check_db_connection()
    health_data = HealthStatus(
        status="healthy" if db_status["connected"] else "degraded",
        database=db_status,
        version="1.0.0"
    )
    return StandardResponse(
        success=db_status["connected"],
        data=health_data,
        error=db_status["error"],
        message="System fully operational" if db_status["connected"] else "Database connection failed"
    )

