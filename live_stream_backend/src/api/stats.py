"""
Statistics API endpoints for logging user's watching and stream interaction events.
Provides endpoints for tracking when users start, stop, or view a stream.

Routes:
- POST /api/stats/watch_start: Register/start a watch session (returns session info)
- POST /api/stats/watch_stop: Log when a user stops watching (returns updated session info)
- POST /api/stats/view: Log a generic stats event (such as total watched_seconds/quality rating)

All endpoints are grouped under the "Statistics" OpenAPI tag.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from src.db import SessionLocal
from src.models import User, WatchSession, Stat
from src.schemas import WatchSessionCreate, WatchSessionRead, StatCreate, StatRead

router = APIRouter(prefix="/api/stats", tags=["Statistics"])

# --- Dependency to get DB session ---
# PUBLIC_INTERFACE
def get_db():
    """Yield SQLAlchemy DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Helper function to get a user by ID (simulate authentication) ---
def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

# PUBLIC_INTERFACE
@router.post(
    "/watch_start",
    response_model=WatchSessionRead,
    summary="Start watching a stream",
    description="Register when a user starts watching a stream. Returns a WatchSession.",
    responses={
        200: {"description": "Session started"},
        400: {"description": "User not found"},
    },
)
def watch_start(
    data: WatchSessionCreate,
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Start a watching session for a given stream and user.
    user_id: The user's ID (should be taken from authentication in a real-world scenario).
    """
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")
    session = WatchSession(user_id=db_user.id, stream_id=data.stream_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

# PUBLIC_INTERFACE
@router.post(
    "/watch_stop",
    response_model=WatchSessionRead,
    summary="Stop watching a stream",
    description="Log when a user stops watching a stream. Sets ended_at value and returns updated session.",
    responses={
        200: {"description": "Session stopped"},
        400: {"description": "Session/User not found"},
    },
)
def watch_stop(
    session_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Mark a watch session as stopped by setting ended_at timestamp.
    """
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")
    session = db.query(WatchSession).filter(
        WatchSession.id == session_id, WatchSession.user_id == db_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=400, detail="Session not found")
    if session.ended_at:
        return session  # Already stopped
    session.ended_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session

# PUBLIC_INTERFACE
@router.post(
    "/view",
    response_model=StatRead,
    summary="Log viewing statistics",
    description="Log per-session stats after or during a watch session (total watched_seconds, action log, and video quality rating).",
    responses={
        200: {"description": "Stat event logged"},
        400: {"description": "User or session not found"},
    },
)
def log_stat(
    stat: StatCreate,
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Add or update stats (watched_seconds, actions, quality) for a session and user.
    """
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")
    session = db.query(WatchSession).filter(
        WatchSession.id == stat.session_id, WatchSession.user_id == db_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=400, detail="Session not found")

    new_stat = Stat(
        user_id=db_user.id,
        session_id=stat.session_id,
        watched_seconds=stat.watched_seconds,
        actions=stat.actions,
        quality_rating=stat.quality_rating,
    )
    db.add(new_stat)
    db.commit()
    db.refresh(new_stat)
    return new_stat
