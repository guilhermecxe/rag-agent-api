from langchain_core.documents import Document
import math
import re

from src.services.pdf_service import PDFService
from src.services.chroma_service import ChromaService
from src.settings import Settings


class SourcesService:
    """Serviço de alto nível para gerenciamento de fontes indexadas.

    Coordena o parsing de PDFs via PDFService e a persistência/busca
    no banco vetorial via ChromaService.

    Attributes:
        _pdf_service (PDFService): Serviço de extração de texto de PDFs.
        _chroma_service (ChromaService): Serviço de armazenamento vetorial.
        _settings (Settings): Configurações da aplicação.
    """

    def __init__(self, pdf_service: PDFService, chroma_service: ChromaService, settings: Settings):
        """Inicializa o SourcesService com suas dependências.

        Args:
            pdf_service (PDFService): Serviço responsável por extrair páginas de PDFs.
            chroma_service (ChromaService): Serviço de banco vetorial Chroma.
            settings (Settings): Configurações da aplicação.
        """
        self._pdf_service = pdf_service
        self._chroma_service = chroma_service
        self._settings = settings

    async def upload(self, source_bytes: bytes, source_title: str, source_type: str):
        """Faz o parse e indexa uma fonte no banco vetorial.

        Args:
            source_bytes (bytes): Conteúdo binário da fonte.
            source_title (str): Nome/título da fonte usado como chave nos metadados.
            source_type (str): Tipo da fonte. Atualmente apenas ``"pdf"`` é suportado.

        Raises:
            ValueError: Se já existir uma fonte com o mesmo título.
            NotImplementedError: Se ``source_type`` não for ``"pdf"``.
        """
        if self.source_title_exists(source_title=source_title):
            raise ValueError("Já existe uma fonte com este nome.")

        if source_type == "pdf":
            documents = self._pdf_service.read(pdf_bytes=source_bytes, pdf_title=source_title)
            await self._chroma_service.add_documents(documents)
        else:
            raise NotImplementedError(f"There is no support to {source_type} type yet.")

    def get_sources(self, page: int = 1) -> dict:
        """Retorna os títulos de todas as fontes indexadas.

        Returns:
            list[str]: Lista de títulos únicos presentes no banco vetorial.
        """
        sources_per_page = 10
        sources = self._chroma_service.get_unique_titles()

        if not sources:
            return {
                "sources": [],
                "current_page": 0,
                "last_page": 0,
            }

        first_index = sources_per_page*(page-1)
        last_index = first_index + sources_per_page

        if first_index+1 > len(sources):
            raise ValueError("Essa página não existe para a busca feita.")

        page_sources = sources[first_index:last_index]

        return {
            "sources": page_sources,
            "current_page": page,
            "last_page": math.ceil(len(sources) / sources_per_page)
        }

    def search_sources_regex(self, pattern: str, page: int = 1) -> dict:
        """Busca fontes cujo título corresponde a um padrão regex.

        Args:
            pattern (str): Expressão regular aplicada ao título das fontes.
            page (int): Página de resultados a retornar. Padrão: ``1``.

        Returns:
            dict: Dicionário com as chaves:
                - ``relevant_sources`` (list[str]): Títulos da página atual.
                - ``current_page`` (int): Número da página atual.
                - ``last_page`` (int): Número da última página disponível.

        Raises:
            ValueError: Se ``page`` estiver além do número de páginas disponíveis.
        """
        sources_per_page = 10
        sources = self._chroma_service.get_unique_titles()

        relevant_sources = []
        for source in sources:
            if re.search(pattern, source, flags=re.IGNORECASE):
                relevant_sources.append(source)

        if not relevant_sources:
            return {
                "relevant_sources": [],
                "current_page": 0,
                "last_page": 0,
            }

        first_page_source_index = sources_per_page*(page-1)
        last_page_source_index = first_page_source_index + sources_per_page

        if first_page_source_index+1 > len(relevant_sources):
            raise ValueError("Essa página não existe para a busca feita.")

        page_relevant_sources = relevant_sources[first_page_source_index:last_page_source_index]

        return {
            "relevant_sources": page_relevant_sources,
            "current_page": page,
            "last_page": math.ceil(len(relevant_sources) / sources_per_page)
        }

    def get_excerpt(self, source_name: str, index: int) -> Document:
        """Retorna um trecho específico de uma fonte pelo seu índice incremental.

        Args:
            source_name (str): Título da fonte de origem.
            index (int): Índice incremental da página (base 1), conforme armazenado
                nos metadados pelo PDFService.

        Returns:
            Document: Trecho correspondente ao par ``(source_name, index)``.

        Raises:
            ValueError: Se não existir trecho com os parâmetros fornecidos.
        """
        return self._chroma_service.get_excerpt(source_name=source_name, index=index)

    def search_excerpts_regex(
        self, pattern: str, sources: list[str] | None = None, page: int = 1
    ) -> dict:
        """Busca trechos de documentos cujo conteúdo corresponde a um padrão regex.

        Args:
            pattern (str): Expressão regular aplicada ao conteúdo dos documentos.
            sources (list[str] | None): Títulos de fontes que limitam a busca.
                Se ``None``, busca em todas as fontes indexadas.
            page (int): Página de resultados a retornar. Padrão: ``1``.

        Returns:
            dict: Dicionário com as chaves:
                - ``relevant_excerpts`` (list[Document]): Documentos da página atual.
                - ``current_page`` (int): Número da página atual.
                - ``last_page`` (int): Número da última página disponível.

        Raises:
            ValueError: Se ``page`` estiver além do número de páginas disponíveis.
        """
        excerpts_per_page = 5
        excerpts = self._chroma_service.search_excerpts_regex(
            pattern=pattern, sources=sources
        )

        if not excerpts:
            return {
                "relevant_excerpts": [],
                "current_page": 0,
                "last_page": 0,
            }

        first = excerpts_per_page * (page - 1)
        last = first + excerpts_per_page

        if first + 1 > len(excerpts):
            raise ValueError("Essa página não existe para a busca feita.")

        return {
            "relevant_excerpts": excerpts[first:last],
            "current_page": page,
            "last_page": math.ceil(len(excerpts) / excerpts_per_page),
        }

    def delete_source(self, source_title: str):
        """Remove todos os documentos de uma fonte do banco vetorial.

        Args:
            source_title (str): Título da fonte a excluir.
        """
        self._chroma_service.delete_documents(title=source_title)

    def source_title_exists(self, source_title: str) -> bool:
        """Verifica se uma fonte já está indexada.

        Args:
            source_title (str): Título a verificar.

        Returns:
            bool: ``True`` se existir, ``False`` caso contrário.
        """
        return self._chroma_service.document_exists(title=source_title)

    def search_excerpts_semantic(
        self, query: str, source_names: list[str] | None = None
    ) -> list[Document]:
        """Busca trechos de documentos semanticamente similares à query.

        Usa similaridade de embeddings para encontrar os trechos mais relevantes.

        Args:
            query (str): Texto da consulta.
            source_names (list[str] | None): Títulos de fontes que limitam a busca.
                Se ``None``, busca em todas as fontes indexadas.

        Returns:
            list[Document]: Trechos mais relevantes encontrados.
        """
        return self._chroma_service.search_excerpts_semantic(
            query=query,
            source_names=source_names,
            limit=5,
        )

    def search_documents(self, query: str, limit: int = 5) -> list[Document]:
        """Busca documentos semanticamente similares à query.

        Args:
            query (str): Texto da consulta.
            limit (int): Número máximo de documentos retornados. Padrão: ``5``.

        Returns:
            list[Document]: Documentos mais relevantes encontrados no banco vetorial.
        """
        return self._chroma_service.search_documents(query=query, limit=limit)
