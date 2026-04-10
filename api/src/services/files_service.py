from langchain_core.documents import Document

from src.services.pdf_service import PDFService
from src.services.chroma_service import ChromaService


class FilesService:
    def __init__(self, pdf_service: PDFService, chroma_service: ChromaService):
        self._pdf_service = pdf_service
        self._chroma_service = chroma_service

    def upload(self, file_bytes: bytes, file_title: str, file_type: str):
        if self.file_title_exists(file_title=file_title):
            raise ValueError("Já existe um arquivo com este nome.")

        if file_type == "pdf":
            documents = self._pdf_service.read(pdf_bytes=file_bytes, pdf_title=file_title)
            self._chroma_service.add_documents(documents)
        else:
            raise NotImplementedError(f"There is no support to {file_type} type yet.")

    def get_files(self) -> list[str]:
        return self._chroma_service.get_unique_titles()

    def delete_file(self, file_title: str):
        self._chroma_service.delete_documents(title=file_title)
    
    def file_title_exists(self, file_title: str) -> bool:
        return self._chroma_service.document_exists(title=file_title)

    def search_documents(self, query: str, limit: int = 5) -> list[Document]:
        return self._chroma_service.search_documents(query=query, limit=limit)