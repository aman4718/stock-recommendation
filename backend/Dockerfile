# Use a stable Python version that has pre-built wheels for pandas/torch
FROM python:3.11-slim

# Install system dependencies needed for building some packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Step 1: Install CPU-only PyTorch first to save massive amounts of space (approx 2GB vs 5GB+)
# This prevents the default GPU-enabled torch from being installed by dependencies.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Step 2: Install other requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Expose the port Railway provides (default is 8000 for FastAPI)
ENV PORT=8000
EXPOSE 8000

# Start the application using uvicorn via a shell to evaluate the $PORT variable correctly
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
