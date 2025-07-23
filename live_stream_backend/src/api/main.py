from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response

import os

from src.api.auth import router as auth_router
from src.api.stats import router as stats_router
from src.api.metrics import router as metrics_router

app = FastAPI(
    title="Live Stream Platform Backend",
    description="FastAPI backend for live stream platform: auth, stats, metrics.",
    version="0.1.0"
)

# --- Configure CORS ---
# In production, restrict origins appropriately
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN] if FRONTEND_ORIGIN != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Mount React build directory (production) ---
# Assume React build files are output to live_stream_frontend/build
# Adjust the path as per your deployment - here we expect ../live_stream_frontend/build
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(backend_dir, '..', '..', '..'))
react_build_dir = os.path.join(project_root, "live_stream_frontend", "build")
if os.path.exists(react_build_dir):
    app.mount("/static", StaticFiles(directory=os.path.join(react_build_dir, "static")), name="static")
    # Serve main index.html and let React handle routes
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_react_app(full_path: str, request: Request):
        """
        Serve the React SPA index.html for any non-API route (client-side routing).
        """
        # Only handle if not /api or /static
        if full_path.startswith("api") or full_path.startswith("static") or full_path == "favicon.ico":
            return Response(status_code=404)
        index_file = os.path.join(react_build_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file, media_type="text/html")
        return Response(content="Frontend not built", status_code=500)
    # Optionally, serve / (root) as index.html too
    @app.get("/", include_in_schema=False)
    async def root():
        """Return React frontend index.html at root."""
        index_file = os.path.join(react_build_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file, media_type="text/html")
        return Response(content="Frontend not built", status_code=500)
else:
    # Fallback health check (for dev or first-time setup)
    @app.get("/", summary="Health Check", tags=["Health"])
    def health_check():
        """Check that the server is healthy and responsive (no frontend build present)."""
        return {"message": "Healthy (React build directory not found)"}

# Register authentication API router
app.include_router(auth_router)
# Register statistics API router
app.include_router(stats_router)
# Register metrics API router
app.include_router(metrics_router)
