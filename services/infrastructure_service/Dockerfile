# Infrastructure Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY services/infrastructure_service/ ./services/infrastructure_service/

WORKDIR /app/backend

ENV DEPLOYMENT_MODE=microservices
ENV SERVICE_NAME=infrastructure
ENV PORT=8007

EXPOSE 8007

CMD ["python", "-m", "services.infrastructure_service.app"]

