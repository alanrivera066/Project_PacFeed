# Versión fija de imagen base
FROM python:3.12.4-slim

# Sin root
RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

USER appuser

EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/salud')"

CMD ["python", "app.py"]
