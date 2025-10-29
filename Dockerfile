# Backend
FROM python:3.11 as backend

WORKDIR /app/backend

COPY backend/requirements-docker.txt ./requirements.txt

COPY backend/ .

# Frontend
FROM node:16 as frontend

WORKDIR /app/frontend

COPY frontend/ .

# Final image
FROM python:3.8-slim

WORKDIR /app

COPY --from=backend /app/backend .
COPY --from=frontend /app/frontend ./frontend
COPY --from=backend /app/backend/requirements-docker.txt ./requirements-docker.txt
RUN ls -la /app && ls -la /app/frontend && pip install --no-cache-dir -r requirements-docker.txt && pip freeze

RUN apt-get update && apt-get install -y curl gnupg && \
    curl -sSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor > /usr/share/keyrings/cloud.google.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" > /etc/apt/sources.list.d/google-cloud-sdk.list && \
    apt-get update && apt-get install -y google-cloud-sdk openssh-client && \
    apt-get clean

COPY credentials.json /app/credentials.json
RUN gcloud auth activate-service-account --key-file=/app/credentials.json && \
    gcloud config set project augmented-audio-474107-v3

COPY google_compute_engine /root/.ssh/google_compute_engine
COPY google_compute_engine.pub /root/.ssh/google_compute_engine.pub
RUN chmod 600 /root/.ssh/google_compute_engine && chmod 644 /root/.ssh/google_compute_engine.pub

EXPOSE 27015

CMD ["python3", "main.py"]
