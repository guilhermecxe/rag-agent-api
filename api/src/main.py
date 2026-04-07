from fastapi import FastAPI
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up the RAG Agent API...")
    yield
    print("Shutting down the RAG Agent API...")


app = FastAPI(
    title="RAG Agent API",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "Welcome to the RAG Agent API!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
