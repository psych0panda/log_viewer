# Backend
FROM python:3.8-slim as backend

WORKDIR /app/backend

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Frontend
FROM node:16 as frontend

WORKDIR /app/frontend

COPY frontend/ .

# Final image
FROM python:3.8-slim

WORKDIR /app

COPY --from=backend /app/backend .
COPY --from=frontend /app/frontend/ ./frontend
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 27015

CMD ["python", "main.py"]
