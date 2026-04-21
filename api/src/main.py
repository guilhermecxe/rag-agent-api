from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
import logging

from .routes import files_routes, agent_routes


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
    print("Starting up the RAG Agent API...")
    yield
    print("Shutting down the RAG Agent API...")


app = FastAPI(
    title="RAG Agent API",
    lifespan=lifespan
)

app.include_router(files_routes.router, prefix="/api/files", tags=["files"])
app.include_router(agent_routes.router, prefix="/api/agent", tags=["agent"])

@app.get("/")
async def root():
    return {"message": "Welcome to the RAG Agent API!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
