FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Instalando dependências do Python
COPY pyproject.toml uv.lock ./
COPY frontend/pyproject.toml frontend/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --package frontend --no-dev

# Copiando o código da aplicação
COPY frontend/ frontend/

# Expondo a porta da aplicação
EXPOSE 8501

# Comando para rodar a aplicação
CMD ["uv", "run", "--package", "frontend", "streamlit", "run", "frontend/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
