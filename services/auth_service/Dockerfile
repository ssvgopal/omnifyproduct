# Auth Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code (shared)
COPY backend/ ./backend/

# Copy service-specific code
COPY services/auth_service/ ./services/auth_service/

# Set working directory to backend for imports
WORKDIR /app/backend

# Set environment variables
ENV DEPLOYMENT_MODE=microservices
ENV SERVICE_NAME=auth
ENV PORT=8001

# Expose port
EXPOSE 8001

# Run service
CMD ["python", "-m", "services.auth_service.app"]

