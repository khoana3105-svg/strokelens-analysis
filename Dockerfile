FROM node:24-slim AS frontend
WORKDIR /build/frontend
COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM python:3.14-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements-lock.txt ./
RUN pip install --no-cache-dir -r requirements-lock.txt
COPY backend/ ./backend/
COPY artifacts/ ./artifacts/
COPY docs/provenance.json ./docs/provenance.json
COPY --from=frontend /build/frontend/dist ./frontend/dist
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4)"
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
