# MPLADS AI RiskIntel — Backend API (FastAPI + SQLite)
# Persistent-server deployment: the real eSAKSHI dataset is too large for
# serverless functions, so the API runs as a long-lived container with a
# volume-persisted SQLite database.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLADS_DB=/data/mplads.db \
    PYTHONPATH=/app/backend

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY backend/ ./backend/

# Real eSAKSHI dataset (CSVs) — the ETL builds the SQLite database from these
COPY data/mplads_data/csv/ ./data/mplads_data/csv/

# Persistent volume for the built database (and its WAL sidecars)
VOLUME ["/data"]

EXPOSE 8000

# Build the database on first boot (if the volume is empty), then serve
CMD ["bash", "-c", "\
  if [ ! -f /data/mplads.db ]; then \
    echo '[entrypoint] No database found on volume — running ETL over the real eSAKSHI CSVs (this takes a few minutes)...'; \
    python -m app.etl; \
  else \
    echo '[entrypoint] Existing database found on volume — skipping ETL.'; \
  fi && \
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]
