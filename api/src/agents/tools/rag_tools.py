from langchain_core.tools import StructuredTool
from langchain.tools import tool

from src.services.sources_service import SourcesService
from src.settings import Settings

class RAGToolkit:
    """Conjunto de ferramentas LangChain disponibilizadas ao agente RAG.

    Attributes:
        _sources_service (SourcesService): Serviço de acesso ao banco de documentos.
        _search_documents_limit (int): Número máximo de resultados por busca.
    """

    def __init__(self, sources_service: SourcesService, settings: Settings):
        """Inicializa o toolkit com o serviço de sources e o limite de busca.

        Args:
            sources_service (SourcesService): Serviço usado para recuperar documentos.
            settings (Settings): Configurações com o limite de documentos retornados.
        """
        self._sources_service = sources_service
        self._search_documents_limit = settings.search_documents_limit

    def _search_documents(self, query: str) -> list[dict]:
        """Realiza uma busca semântica no banco vetorial e retorna os documentos mais relevantes.

        Usa similaridade de embeddings para encontrar trechos de documentos
        relacionados à ``query``, independentemente de correspondência literal.

        Args:
            query (str): Texto da consulta a ser pesquisada semanticamente.

        Returns:
            list[dict]: Lista de dicionários com as chaves:
                - ``title`` (str): Título da fonte de origem.
                - ``content`` (str): Trecho de texto do documento.
        """
        documents = self._sources_service.search_documents(
            query=query, limit=self._search_documents_limit
        )

        formatted_documents = []
        for doc in documents:
            formatted_documents.append({
                "title": doc.metadata["title"],
                "content": doc.page_content
            })

        return formatted_documents

    def get_tools(self) -> list[StructuredTool]:
        """Retorna a lista de ferramentas LangChain registradas no toolkit.

        Returns:
            list[StructuredTool]: Ferramentas prontas para uso pelo agente.
        """
        return [
            StructuredTool.from_function(
                func=self._search_documents,
                name="search_documents",
                description="Search for information on inner database."
            )
        ]
