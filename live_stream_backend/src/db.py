"""
Database initialization module for SQLAlchemy/SQLite integration.
Handles engine creation, session management, and base class definition for ORM mapping.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PUBLIC_INTERFACE
def get_database_url():
    """Returns the SQLite database URL."""
    # You may adapt this to read from .env if needed.
    return "sqlite:///./live_stream.db"

SQLALCHEMY_DATABASE_URL = get_database_url()

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal instance for dependency injection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for models
Base = declarative_base()
