FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Instalando dependências do Python
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

# Copiando o código da aplicação
COPY . .

# Expondo a porta da aplicação
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]