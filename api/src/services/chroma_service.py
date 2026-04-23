from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document

from src.settings import Settings

class ChromaService:
    """Serviço de acesso ao banco de dados vetorial Chroma.

    Encapsula operações de persistência, busca e gerenciamento de documentos
    usando a coleção configurada em Settings.

    Attributes:
        _embedding_function (Embeddings): Função de embedding usada pelo vector store.
        _settings (Settings): Configurações com nome da coleção e diretório de persistência.
        _vector_store (Chroma): Instância do armazenamento vetorial.
    """

    def __init__(self, embedding_function: Embeddings, settings: Settings):
        """Inicializa o ChromaService e conecta à coleção configurada.

        Args:
            embedding_function (Embeddings): Função de embedding para vetorizar
                documentos e queries.
            settings (Settings): Configurações com ``chroma_collection_name`` e
                ``chroma_persist_directory``.
        """
        self._embedding_function = embedding_function
        self._settings = settings

        self._vector_store = Chroma(
            collection_name=self._settings.chroma_collection_name,
            embedding_function=self._embedding_function,
            persist_directory=self._settings.chroma_persist_directory,
        )

    def add_documents(self, documents: list[Document]):
        """Adiciona documentos ao banco vetorial.

        Args:
            documents (list[Document]): Lista de Documents LangChain a indexar.
        """
        self._vector_store.add_documents(documents)

    def get_unique_titles(self) -> list[str]:
        """Retorna os títulos únicos de todos os documentos armazenados.

        Returns:
            list[str]: Lista de títulos sem duplicatas, extraídos dos metadados.
        """
        collection = self._vector_store.get(include=["metadatas"])
        titles = [doc["title"] for doc in collection["metadatas"]]
        return list(set(titles))

    def delete_documents(self, title: str):
        """Remove todos os documentos com o título fornecido.

        Args:
            title (str): Título dos documentos a excluir.
        """
        collection = self._vector_store.get(
            include=[],
            where={"title": title}
        )
        self._vector_store.delete(ids=collection["ids"])

    def document_exists(self, title: str) -> bool:
        """Verifica se existe ao menos um documento com o título fornecido.

        Args:
            title (str): Título a pesquisar.

        Returns:
            bool: ``True`` se existir, ``False`` caso contrário.
        """
        return bool(
            self._vector_store.get(
                include=[], where={"title": title}, limit=1)
            ["ids"]
        )

    def get_excerpt(self, source_name: str, index: int) -> Document:
        """Retorna o trecho de um documento identificado pelo título e índice.

        Args:
            source_name (str): Título do arquivo de origem.
            index (int): Índice incremental da página (base 1).

        Returns:
            Document: Documento correspondente ao par ``(source_name, index)``.

        Raises:
            ValueError: Se nenhum documento for encontrado para os parâmetros fornecidos.
        """
        result = self._vector_store.get(
            where={"$and": [{"title": {"$eq": source_name}}, {"index": {"$eq": index}}]},
            include=["documents", "metadatas"],
        )
        if not result["documents"]:
            raise ValueError(
                f"Nenhum trecho encontrado para source_name='{source_name}', index={index}."
            )
        return Document(
            page_content=result["documents"][0],
            metadata=result["metadatas"][0],
        )

    def search_excerpts_regex(
        self, pattern: str, sources: list[str] | None = None
    ) -> list[Document]:
        """Busca documentos cujo conteúdo corresponde a um padrão regex.

        Args:
            pattern (str): Expressão regular aplicada ao conteúdo dos documentos.
            sources (list[str] | None): Títulos de arquivos que limitam a busca.
                Se ``None``, busca em todos os documentos.

        Returns:
            list[Document]: Documentos cujo conteúdo corresponde ao padrão.
        """
        where = {"title": {"$in": sources}} if sources else None
        result = self._vector_store.get(
            where=where,
            where_document={"$regex": pattern},
            include=["documents", "metadatas"],
        )
        return [
            Document(page_content=content, metadata=metadata)
            for content, metadata in zip(result["documents"], result["metadatas"])
        ]

    def search_excerpts_semantic(
        self, query: str, limit: int, source_names: list[str] | None = None
    ) -> list[Document]:
        """Busca trechos semanticamente similares à query, com filtro opcional por fonte.

        Args:
            query (str): Texto da consulta.
            limit (int): Número máximo de resultados.
            source_names (list[str] | None): Títulos de arquivos que limitam a busca.
                Se ``None``, busca em todos os documentos.

        Returns:
            list[Document]: Trechos mais similares à query.
        """
        filter_ = {"title": {"$in": source_names}} if source_names else None
        return self._vector_store.similarity_search(query=query, k=limit, filter=filter_)

    def search_documents(self, query: str, limit: int) -> list[Document]:
        """Busca documentos semanticamente similares à query.

        Args:
            query (str): Texto da consulta.
            limit (int): Número máximo de resultados.

        Returns:
            list[Document]: Documentos mais similares à query.
        """
        return self._vector_store.similarity_search(query=query, k=limit)
