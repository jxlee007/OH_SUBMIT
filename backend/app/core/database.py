"""Database setup and session management."""
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.app.core.config import settings

# Create engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for obtaining database sessions per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> dict:
    """Verifies live PostgreSQL connection status."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar()
            return {"connected": True, "ping": result, "error": None}
    except Exception as exc:
        return {"connected": False, "ping": None, "error": str(exc)}


def create_tables() -> None:
    """Create all SQLAlchemy-mapped tables (idempotent)."""
    # Import all models so their metadata is registered before create_all
    from backend.app.models import user, product, subscription, invoice, payment  # noqa: F401
    Base.metadata.create_all(bind=engine)
