# Use a stable Python version that has pre-built wheels for pandas/torch
FROM python:3.11-slim

# Install system dependencies needed for building some packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Expose the port Railway provides
ENV PORT=8000
EXPOSE 8000

# Start the application using uvicorn
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
