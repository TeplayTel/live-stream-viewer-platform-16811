"""
Pydantic schemas for validation/serialization of API request and response data.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# -------------------- User Schemas --------------------
# PUBLIC_INTERFACE
class UserBase(BaseModel):
    """
    Shared fields for user.
    """
    username: str = Field(..., description="Unique username")
    email: EmailStr = Field(..., description="User email address")

# PUBLIC_INTERFACE
class UserCreate(UserBase):
    password: str = Field(..., description="Password for registration")

# PUBLIC_INTERFACE
class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# -------------------- Watch Session Schemas --------------------
# PUBLIC_INTERFACE
class WatchSessionBase(BaseModel):
    stream_id: str = Field(..., description="Stream identifier")

# PUBLIC_INTERFACE
class WatchSessionCreate(WatchSessionBase):
    pass

# PUBLIC_INTERFACE
class WatchSessionRead(WatchSessionBase):
    id: int
    user_id: int
    started_at: datetime
    ended_at: Optional[datetime]

    class Config:
        orm_mode = True

# -------------------- Stats Schemas --------------------
# PUBLIC_INTERFACE
class StatBase(BaseModel):
    watched_seconds: int = Field(..., description="Number of seconds watched")
    actions: Optional[str] = Field(None, description="Serialized action log")
    quality_rating: Optional[float] = Field(None, description="Video quality rating")

# PUBLIC_INTERFACE
class StatCreate(StatBase):
    session_id: int

# PUBLIC_INTERFACE
class StatRead(StatBase):
    id: int
    user_id: int
    session_id: int

    class Config:
        orm_mode = True
