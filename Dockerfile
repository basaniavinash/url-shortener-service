# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# install system deps needed for psycopg2-binary (libpq) and build wheels if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 gcc build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# requirements first (better layer caching)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# app code last
COPY app ./app

# create non-root user/group
RUN addgroup --system app && adduser --system --ingroup app app \
 && chown -R app:app /app

USER app

EXPOSE 8000

# NOTE: gunicorn manages worker lifecycle; uvicorn is the ASGI worker
# tune workers/threads for your CPU later
CMD ["gunicorn", "app.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", "--threads", "2", \
     "--access-logfile", "-", "--error-logfile", "-"]
