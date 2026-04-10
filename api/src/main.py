from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from .routes import files_routes


load_dotenv()

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


@app.get("/")
async def root():
    return {"message": "Welcome to the RAG Agent API!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
