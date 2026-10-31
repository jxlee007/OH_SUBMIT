"""Pytest configuration and shared fixtures."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.database import Base, get_db
from backend.app.core.security import create_access_token
from backend.app.main import app

# SQLite in-memory with StaticPool so in-memory DB persists across connections in test
SQLALCHEMY_TEST_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine(
        SQLALCHEMY_TEST_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Import all models so metadata is registered
    from backend.app.models import user, product, plan, subscription, invoice, payment, discount, password_reset, quotation_template, variant  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Database kernel triggers for paid invoice immutability
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS trg_protect_paid_invoices_update
            BEFORE UPDATE ON invoices
            BEGIN
                SELECT CASE WHEN OLD.status = 'paid' THEN RAISE (ABORT, 'Database Violation: Invoices in paid status are immutable and cannot be updated.') END;
            END;
        """))
        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS trg_protect_paid_invoices_delete
            BEFORE DELETE ON invoices
            BEGIN
                SELECT CASE WHEN OLD.status = 'paid' THEN RAISE (ABORT, 'Database Violation: Invoices in paid status are immutable and cannot be deleted.') END;
            END;
        """))
        conn.commit()

    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
    session = Session()
    yield session
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(db_session):
    """Create an admin user and return their bearer token."""
    from backend.app.models.user import User as UserModel
    from backend.app.core.security import hash_password
    user = UserModel(
        email="admin@test.com",
        hashed_password=hash_password("Admin@1234"),
        full_name="Admin User",
        role="admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return create_access_token({"sub": str(user.id), "role": "admin"})


@pytest.fixture
def staff_token(db_session):
    """Create a staff user and return their bearer token."""
    from backend.app.models.user import User as UserModel
    from backend.app.core.security import hash_password
    user = UserModel(
        email="staff@test.com",
        hashed_password=hash_password("Staff@1234"),
        full_name="Staff User",
        role="staff",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return create_access_token({"sub": str(user.id), "role": "staff"})


@pytest.fixture
def customer_token(db_session):
    """Create a customer user and return their bearer token."""
    from backend.app.models.user import User as UserModel
    from backend.app.core.security import hash_password
    user = UserModel(
        email="customer@test.com",
        hashed_password=hash_password("Customer@1234"),
        full_name="Test Customer",
        role="customer",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return create_access_token({"sub": str(user.id), "role": "customer"})
