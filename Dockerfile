FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Instala dependências mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instala as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia a aplicação
COPY app/ ./app
COPY .env .

# Executa o script principal
CMD ["python", "app/main.py"]
