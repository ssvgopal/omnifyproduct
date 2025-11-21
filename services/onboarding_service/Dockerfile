# Onboarding Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY services/onboarding_service/ ./services/onboarding_service/

WORKDIR /app/backend

ENV DEPLOYMENT_MODE=microservices
ENV SERVICE_NAME=onboarding
ENV PORT=8005

EXPOSE 8005

CMD ["python", "-m", "services.onboarding_service.app"]

