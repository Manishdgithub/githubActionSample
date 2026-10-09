FROM node:20-alpine AS frontend-builder
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS runner
WORKDIR /app

RUN addgroup --system appgroup && adduser --system --group appuser

COPY pyproject.toml .
COPY src/ ./src/
RUN pip install --no-cache-dir .

COPY --from=frontend-builder /build/dist ./frontend/dist

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')" || exit 1

CMD ["uvicorn", "enterprise_hub.app:app", "--host", "0.0.0.0", "--port", "8000"]
