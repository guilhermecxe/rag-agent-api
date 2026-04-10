from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document

from src.settings import Settings

class ChromaService:
    def __init__(self, embedding_function: Embeddings, settings: Settings):
        self._embedding_function = embedding_function
        self._settings = settings

        self._vector_store = Chroma(
            collection_name=self._settings.chroma_collection_name,
            embedding_function=self._embedding_function,
            persist_directory=self._settings.chroma_persist_directory,
        )

    def add_documents(self, documents: list[Document]):
        self._vector_store.add_documents(documents)

    def get_unique_titles(self) -> list[str]:
        collection = self._vector_store.get(include=["metadatas"])
        titles = [doc["title"] for doc in collection["metadatas"]]
        return list(set(titles))

    def delete_documents(self, title: str):
        collection = self._vector_store.get(
            include=[],
            where={"title": title}
        )
        self._vector_store.delete(ids=collection["ids"])

    def document_exists(self, title: str):
        return bool(
            self._vector_store.get(
                include=[], where={"title": title}, limit=1)
            ["ids"]
        )

    def search_documents(self, query: str, limit: int):
        return self._vector_store.similarity_search(query=query, k=limit)
