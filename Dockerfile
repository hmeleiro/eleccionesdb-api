# ── Build stage ──────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Final stage ─────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Sólo libpq en runtime (no gcc)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copiar dependencias instaladas
COPY --from=builder /install /usr/local

# Copiar código de la aplicación
COPY app/ app/

EXPOSE 8000

# No usar --reload en producción
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
