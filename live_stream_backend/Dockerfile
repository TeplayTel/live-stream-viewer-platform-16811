# Dockerfile for FastAPI Backend (live_stream_backend)

FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies required for some Python packages
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (only requirements.txt to leverage Docker cache)
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (rest of the backend)
COPY ./src ./src

# Expose FastAPI default port
EXPOSE 8000

# Set environment variables for production (optional, can use .env at runtime)
ENV PYTHONUNBUFFERED=1

# Command to run FastAPI app using uvicorn (app variable in src/api/main.py)
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
