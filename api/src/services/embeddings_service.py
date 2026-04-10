from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings

from src.settings import Settings

class EmbeddingsService:
    def __init__(self, settings: Settings):
        self._settings = settings

    def get_embeddings(self, model_name: str | None = None) -> Embeddings:
        if model_name is None:
            model_name = self._settings.embedding_model_name
        return HuggingFaceEmbeddings(model_name=model_name)
