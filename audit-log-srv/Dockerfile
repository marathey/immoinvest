# backend/Dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/src

ENV PYTHONUNBUFFERED=1  

# Copy .env file (if applicable)
COPY .env /app/

EXPOSE 8000
CMD ["python", "src/main.py"]