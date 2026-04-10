from fastapi import Depends
from functools import lru_cache

from src.settings import Settings
from src.services.embeddings_service import EmbeddingsService
from src.services.chroma_service import ChromaService
from src.services.files_service import FilesService
from src.services.pdf_service import PDFService


@lru_cache()
def get_settings() -> Settings:
    return Settings()

def get_embeddings_service(settings: Settings = Depends(get_settings)) -> EmbeddingsService:
    return EmbeddingsService(settings=settings)

def get_chroma_service(
        embeddings_service: EmbeddingsService = Depends(get_embeddings_service),
        settings: Settings = Depends(get_settings)
    ) -> ChromaService:
    return ChromaService(
        embedding_function=embeddings_service.get_embeddings(),
        settings=settings
    )

def get_pdf_service():
    return PDFService()

def get_files_service(
        chroma_service: ChromaService = Depends(get_chroma_service),
        pdf_service: PDFService = Depends(get_pdf_service)
    ) -> FilesService:
    return FilesService(pdf_service=pdf_service, chroma_service=chroma_service)