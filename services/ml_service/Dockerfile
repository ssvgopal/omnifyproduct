# ML Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY services/ml_service/ ./services/ml_service/

WORKDIR /app/backend

ENV DEPLOYMENT_MODE=microservices
ENV SERVICE_NAME=ml
ENV PORT=8006

EXPOSE 8006

CMD ["python", "-m", "services.ml_service.app"]

