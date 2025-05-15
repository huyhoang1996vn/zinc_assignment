# Stage 1: Build and install dependencies
FROM python:3.11-slim

# Install build essentials for mysqlclient and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

# Adjust main:app, workers, or other Gunicorn settings as needed.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
