"""
Metrics API endpoint for live stream backend.

Provides:
- /api/metrics: Real-time application and viewer statistics for health dashboards and monitoring.

Metrics include:
- Total active viewers (watch sessions that have started and not yet ended)
- Total sessions
- Total stats events
- Application health (simple database check)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db import SessionLocal
from src.models import WatchSession, Stat, User
from pydantic import BaseModel, Field

# Define router
router = APIRouter(prefix="/api/metrics", tags=["Metrics"])


# PUBLIC_INTERFACE
def get_db():
    """
    FastAPI dependency for DB session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic schema for the metrics response
# PUBLIC_INTERFACE
class MetricsResponse(BaseModel):
    """
    Overall live streaming backend metrics.
    """
    total_active_viewers: int = Field(..., description="Count of active watch sessions (viewers currently watching)")
    total_sessions: int = Field(..., description="Total watch sessions ever started")
    total_stats: int = Field(..., description="Total statistics/events logged")
    total_users: int = Field(..., description="Total registered users")
    db_ok: bool = Field(..., description="Database health (True=operational)")
    health: str = Field(..., description="Application health summary")

# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=MetricsResponse,
    summary="Get real-time metrics and health status",
    description="Return total viewer count, stats, and application health.",
    tags=["Metrics"],
    responses={200: {"description": "Metrics and health overview"}}
)
def get_metrics(db: Session = Depends(get_db)):
    """
    Get current metrics: viewer count, session count, stats, users, and health.
    Returns a MetricsResponse with up-to-date information.
    """
    try:
        # Total active sessions (not ended)
        total_active_viewers = db.query(WatchSession).filter(WatchSession.ended_at == None).count()
        total_sessions = db.query(WatchSession).count()
        total_stats = db.query(Stat).count()
        total_users = db.query(User).count()
        db_ok = True
        health = "healthy"
    except Exception:
        total_active_viewers = 0
        total_sessions = 0
        total_stats = 0
        total_users = 0
        db_ok = False
        health = "unhealthy"
    return MetricsResponse(
        total_active_viewers=total_active_viewers,
        total_sessions=total_sessions,
        total_stats=total_stats,
        total_users=total_users,
        db_ok=db_ok,
        health=health,
    )
