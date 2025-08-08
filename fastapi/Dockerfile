FROM python:3.11-slim

# Instala dependências de sistema para compilação de libs Python
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cria o diretório de trabalho
WORKDIR /app

# Copia os arquivos para dentro da imagem
COPY . .

# Garante que o pacote 'app' seja encontrado
ENV PYTHONPATH=/app

# Instala dependências Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -r test_requirements.txt

# CMD ["tail", "-f", "/dev/null"]
# Inicia o FastAPI com Uvicorn
CMD ["python", "-m", "app.main"]
