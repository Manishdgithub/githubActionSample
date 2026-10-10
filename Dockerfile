FROM node:20-alpine AS frontend-builder
WORKDIR /build
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN chmod -R +x node_modules/.bin && npm run build

FROM python:3.12-slim AS runner
WORKDIR /app

# Create non-root user and persistent /data directory
RUN addgroup --system appgroup && \
    adduser --system --group appuser && \
    mkdir -p /data && \
    chown -R appuser:appgroup /data /app

COPY pyproject.toml .
COPY src/ ./src/
RUN pip install --no-cache-dir .

COPY --from=frontend-builder /build/dist ./frontend/dist

# Switch ownership of installed app files
RUN chown -R appuser:appgroup /app

USER appuser

# Set default SQLite storage path to writable directory
ENV DATABASE_URL="sqlite:////data/prod_hub.db"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')" || exit 1

CMD ["uvicorn", "enterprise_hub.app:app", "--host", "0.0.0.0", "--port", "8000"]
#docker run -d \ -p 8000:8000 \ -v enterprise-data:/data \ ghcr.io/manishdgithub/githubactionsample:latest