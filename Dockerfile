FROM python:3.11-slim

WORKDIR /app

# Instala dependências mínimas
RUN apt-get update && apt-get install -y \
    curl unzip gnupg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app
COPY .env .

CMD ["python", "app/main.py"]
