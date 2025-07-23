"""
Defines the SQLAlchemy ORM models for User, WatchSession, and Stat entities.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from .db import Base

# PUBLIC_INTERFACE
class User(Base):
    """
    User account table.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sessions = relationship("WatchSession", back_populates="user")
    stats = relationship("Stat", back_populates="user")

# PUBLIC_INTERFACE
class WatchSession(Base):
    """
    Table representing individual video watching sessions.
    """
    __tablename__ = "watch_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stream_id = Column(String, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sessions")

# PUBLIC_INTERFACE
class Stat(Base):
    """
    Table for storing user/viewer statistics per session.
    """
    __tablename__ = "stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("watch_sessions.id"), nullable=False)
    watched_seconds = Column(Integer, default=0)
    actions = Column(String, nullable=True)  # JSON or CSV for action logs
    quality_rating = Column(Float, nullable=True)

    user = relationship("User", back_populates="stats")
    # No direct session relationship (for simplicity)
