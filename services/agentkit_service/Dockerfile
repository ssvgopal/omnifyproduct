# AgentKit Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY services/agentkit_service/ ./services/agentkit_service/

WORKDIR /app/backend

ENV DEPLOYMENT_MODE=microservices
ENV SERVICE_NAME=agentkit
ENV PORT=8003

EXPOSE 8003

CMD ["python", "-m", "services.agentkit_service.app"]

