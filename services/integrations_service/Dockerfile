# Integrations Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY services/integrations_service/ ./services/integrations_service/

WORKDIR /app/backend

ENV DEPLOYMENT_MODE=microservices
ENV SERVICE_NAME=integrations
ENV PORT=8002

EXPOSE 8002

CMD ["python", "-m", "services.integrations_service.app"]

