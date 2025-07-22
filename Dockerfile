# Dockerfile
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Copia os arquivos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app

CMD ["python", "app/main.py"]
