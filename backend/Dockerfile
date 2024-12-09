# backend/Dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend .

ENV PYTHONPATH=/app/src

EXPOSE 8000
CMD ["python", "src/main.py"]