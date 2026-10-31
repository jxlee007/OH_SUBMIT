"""Database Initialization and Seeding Script for Demo Data."""
import sys
from pathlib import Path
from urllib.parse import urlparse
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.app.core.config import settings
from backend.app.core.database import SessionLocal, engine, Base

def ensure_database_exists():
    """Ensures the PostgreSQL target database exists, creating it if needed."""
    url = urlparse(settings.DATABASE_URL)
    db_name = url.path.lstrip("/")
    user = url.username or "postgres"
    password = url.password or ""
    host = url.hostname or "localhost"
    port = url.port or 5432

    print(f"Checking PostgreSQL instance at {host}:{port} for database '{db_name}'...")
    try:
        # Connect to default maintenance database 'postgres'
        conn = psycopg2.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cur.fetchone()
            if not exists:
                print(f"Database '{db_name}' not found. Creating database...")
                cur.execute(f'CREATE DATABASE "{db_name}"')
                print(f"Database '{db_name}' created successfully.")
            else:
                print(f"Database '{db_name}' already exists.")
        conn.close()
    except psycopg2.OperationalError as exc:
        print(f"\n[Warning] Could not connect to PostgreSQL default database: {exc}")
        print("Please ensure your PostgreSQL service is running and credentials in backend/.env are accurate.\n")

def seed_data():
    """Initializes tables and seeds initial demo records."""
    ensure_database_exists()
    
    print("Creating all tables in PostgreSQL via SQLAlchemy...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database schema verified.")
    except Exception as exc:
        print(f"Error creating tables: {exc}")
        return

    db = SessionLocal()
    try:
        print("Ready for domain-specific seed data.")
        # Future domain model instances will be populated here
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
