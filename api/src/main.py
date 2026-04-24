from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from langfuse import get_client
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
import logging

from .routes import agents_routes, sources_routes
from .auth import verify_api_key
from .di import get_settings, get_embeddings_service, get_chroma_service, get_sources_service, get_checkpointer


load_dotenv()

# Configurações de log
log_handler = RotatingFileHandler("app.log", maxBytes=1024*1024, backupCount=3)

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    # filename="app.log",     # omita para stdout
    # filemode="a",            # "w" sobrescreve
    encoding="utf-8",
)
logging.getLogger().addHandler(log_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação FastAPI.
    """
    print("Starting up the RAG Agent API...")

    # Warm-up dos serviços
    get_settings()
    get_embeddings_service()
    get_chroma_service()
    get_sources_service()
    get_checkpointer()
    
    app.state.langfuse_client = get_client()

    yield
    print("Shutting down the RAG Agent API...")
    app.state.langfuse_client.flush()


app = FastAPI(
    title="RAG Agent API",
    lifespan=lifespan
)

_auth = [Depends(verify_api_key)]

app.include_router(sources_routes.router, prefix="/api/sources", tags=["sources"], dependencies=_auth)
app.include_router(agents_routes.router, prefix="/api/agents", tags=["agents"], dependencies=_auth)

@app.get("/")
async def root():
    return {"message": "Welcome to the RAG Agent API!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
