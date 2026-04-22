from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from fastapi import Depends, Request
from langfuse import Langfuse
from functools import lru_cache

from src.settings import Settings
from src.services.embeddings_service import EmbeddingsService
from src.services.chroma_service import ChromaService
from src.services.files_service import FilesService
from src.services.pdf_service import PDFService

from src.agents.rag_agent import RAGAgent

@lru_cache()
def get_settings() -> Settings:
    return Settings()

@lru_cache()
def get_embeddings_service() -> EmbeddingsService:
    return EmbeddingsService(settings=get_settings())

@lru_cache()
def get_chroma_service() -> ChromaService:
    embeddings_service = get_embeddings_service()
    return ChromaService(
        embedding_function=embeddings_service.get_embeddings(),
        settings=get_settings()
    )

@lru_cache()
def get_pdf_service():
    return PDFService()

@lru_cache()
def get_files_service() -> FilesService:
    return FilesService(
        pdf_service=get_pdf_service(), chroma_service=get_chroma_service()
    )

def get_langfuse_client(request: Request) -> Langfuse:
    return request.app.state.langfuse_client

# --- Agents ---

@lru_cache()
def get_checkpointer() -> BaseCheckpointSaver:
    return InMemorySaver()

def get_rag_agent(
        files_service: FilesService = Depends(get_files_service),
        settings: Settings = Depends(get_settings)
    ):
    return RAGAgent(files_service, settings, checkpointer=get_checkpointer())
