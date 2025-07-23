"""
Authentication and user management endpoints for the live stream backend.

Provides /api/auth/signup and /api/auth/login using JWT.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from passlib.context import CryptContext
import jwt
from pydantic import BaseModel, Field

from src.db import SessionLocal
from src.models import User as DBUser
from src.schemas import UserCreate, UserRead

import os

# Settings for JWT
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "DEFAULT_JWT_SECRET")
ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# --- Dependency for getting DB session ---
# PUBLIC_INTERFACE
def get_db():
    """FastAPI dependency to get an SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------- JWT Token Schema -------------------
class Token(BaseModel):
    """Returned by login/signup endpoints."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Should be 'bearer'")
    user: UserRead

# -------------Password hashing and verification -------------

def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if password matches hash."""
    return pwd_context.verify(plain_password, hashed_password)

# ---------------JWT Utilities---------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token with provided data and expiry."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_username(db: Session, username: str) -> Optional[DBUser]:
    return db.query(DBUser).filter(DBUser.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[DBUser]:
    return db.query(DBUser).filter(DBUser.email == email).first()

# PUBLIC_INTERFACE
@router.post("/signup", response_model=Token, summary="Register a new user", description="Register a user and return JWT token.")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """Creates a new user account and returns JWT token. Fails if username/email already exists."""
    # Check if username or email is taken
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)
    db_user = DBUser(username=user.username, email=user.email, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Issue JWT
    access_token = create_access_token({"sub": db_user.username, "user_id": db_user.id})
    user_read = UserRead.from_orm(db_user)
    return {"access_token": access_token, "token_type": "bearer", "user": user_read}

class LoginRequest(BaseModel):
    username: str = Field(..., description="User's username or email")
    password: str = Field(..., description="User's password")

# PUBLIC_INTERFACE
@router.post("/login", response_model=Token, summary="Log in a user", description="Authenticate user and return JWT token.")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates a user by username/email and returns a JWT.
    """
    # Allow login by username or email
    db_user = (
        get_user_by_username(db, data.username)
        or get_user_by_email(db, data.username)  # Accept email in "username" field
    )
    if not db_user or not verify_password(data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    # Issue JWT
    access_token = create_access_token({"sub": db_user.username, "user_id": db_user.id})
    user_read = UserRead.from_orm(db_user)
    return {"access_token": access_token, "token_type": "bearer", "user": user_read}
