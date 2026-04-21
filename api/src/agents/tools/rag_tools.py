from langchain_core.tools import StructuredTool
from langchain.tools import tool

from src.services.files_service import FilesService
from src.settings import Settings

class RAGToolkit:
    def __init__(self, files_service: FilesService, settings: Settings):
        self._files_service = files_service
        self._search_documents_limit = settings.search_documents_limit

    def _search_documents(self, query: str):
        """
        Search for information on inner database.
        """
        documents = self._files_service.search_documents(
            query=query, limit=self._search_documents_limit
        )

        formatted_documents = []
        for doc in documents:
            formatted_documents.append({
                "title": doc.metadata["title"],
                "content": doc.page_content
            })

        return formatted_documents

    def get_tools(self):
        return [
            StructuredTool.from_function(
                func=self._search_documents,
                name="search_documents",
                description="Search for information on inner database."
            )
        ]
