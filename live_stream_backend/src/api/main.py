from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.auth import router as auth_router

app = FastAPI(
    title="Live Stream Platform Backend",
    description="FastAPI backend for live stream platform: auth, stats, metrics.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev; change for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register authentication API router
app.include_router(auth_router)

@app.get("/", summary="Health Check", tags=["Health"])
def health_check():
    """Check that the server is healthy and responsive."""
    return {"message": "Healthy"}
