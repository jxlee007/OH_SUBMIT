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
    """Create all SQLAlchemy-mapped tables (idempotent) and apply schema updates."""
    # Import all models so their metadata is registered before create_all
    from backend.app.models import (  # noqa: F401
        user,
        product,
        plan,
        subscription,
        invoice,
        payment,
        discount,
        password_reset,
        quotation_template,
    )
    Base.metadata.create_all(bind=engine)

    # Ensure schema migrations for newly added columns on existing tables
    with engine.connect() as conn:
        migrations = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS token_version INTEGER NOT NULL DEFAULT 1;",
            "ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS quote_valid_until DATE;",
            "ALTER TABLE invoice_lines ADD COLUMN IF NOT EXISTS discount_amount NUMERIC(12, 2) NOT NULL DEFAULT 0.00;",
            "ALTER TABLE plans ADD COLUMN IF NOT EXISTS can_pause BOOLEAN NOT NULL DEFAULT FALSE;",
            "ALTER TABLE plans ADD COLUMN IF NOT EXISTS can_renew BOOLEAN NOT NULL DEFAULT TRUE;",
        ]
        for sql in migrations:
            try:
                conn.execute(text(sql))
            except Exception:
                pass
        conn.commit()
