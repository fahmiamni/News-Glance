FROM python:3.12-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 8080
USER 65534:65534
HEALTHCHECK --interval=60s --timeout=10s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=5)"
CMD ["waitress-serve", "--host=0.0.0.0", "--port=8080", "--threads=16", "app:app"]
