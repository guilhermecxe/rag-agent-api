from langchain_core.documents import Document

from src.services.pdf_service import PDFService
from src.services.chroma_service import ChromaService


class FilesService:
    """Serviço de alto nível para gerenciamento de arquivos indexados.

    Coordena o parsing de PDFs via PDFService e a persistência/busca
    no banco vetorial via ChromaService.

    Attributes:
        _pdf_service (PDFService): Serviço de extração de texto de PDFs.
        _chroma_service (ChromaService): Serviço de armazenamento vetorial.
    """

    def __init__(self, pdf_service: PDFService, chroma_service: ChromaService):
        """Inicializa o FilesService com suas dependências.

        Args:
            pdf_service (PDFService): Serviço responsável por extrair páginas de PDFs.
            chroma_service (ChromaService): Serviço de banco vetorial Chroma.
        """
        self._pdf_service = pdf_service
        self._chroma_service = chroma_service

    def upload(self, file_bytes: bytes, file_title: str, file_type: str):
        """Faz o parse e indexa um arquivo no banco vetorial.

        Args:
            file_bytes (bytes): Conteúdo binário do arquivo.
            file_title (str): Nome/título do arquivo usado como chave nos metadados.
            file_type (str): Tipo do arquivo. Atualmente apenas ``"pdf"`` é suportado.

        Raises:
            ValueError: Se já existir um arquivo com o mesmo título.
            NotImplementedError: Se ``file_type`` não for ``"pdf"``.
        """
        if self.file_title_exists(file_title=file_title):
            raise ValueError("Já existe um arquivo com este nome.")

        if file_type == "pdf":
            documents = self._pdf_service.read(pdf_bytes=file_bytes, pdf_title=file_title)
            self._chroma_service.add_documents(documents)
        else:
            raise NotImplementedError(f"There is no support to {file_type} type yet.")

    def get_files(self) -> list[str]:
        """Retorna os títulos de todos os arquivos indexados.

        Returns:
            list[str]: Lista de títulos únicos presentes no banco vetorial.
        """
        return self._chroma_service.get_unique_titles()

    def delete_file(self, file_title: str):
        """Remove todos os documentos de um arquivo do banco vetorial.

        Args:
            file_title (str): Título do arquivo a excluir.
        """
        self._chroma_service.delete_documents(title=file_title)

    def file_title_exists(self, file_title: str) -> bool:
        """Verifica se um arquivo já está indexado.

        Args:
            file_title (str): Título a verificar.

        Returns:
            bool: ``True`` se existir, ``False`` caso contrário.
        """
        return self._chroma_service.document_exists(title=file_title)

    def search_documents(self, query: str, limit: int = 5) -> list[Document]:
        """Busca documentos semanticamente similares à query.

        Args:
            query (str): Texto da consulta.
            limit (int): Número máximo de documentos retornados. Padrão: ``5``.

        Returns:
            list[Document]: Documentos mais relevantes encontrados no banco vetorial.
        """
        return self._chroma_service.search_documents(query=query, limit=limit)