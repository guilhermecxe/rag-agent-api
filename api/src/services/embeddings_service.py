from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings

from src.settings import Settings

class EmbeddingsService:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._embeddings: dict[str, Embeddings] = {}

    def get_embeddings(self, model_name: str | None = None) -> Embeddings:
        # Se não for especificado, usamos o modelo padrão
        if model_name is None:
            model_name = self._settings.embedding_model_name
        
        # Se não estiver em "cache", carregamos o modelo
        if model_name not in self._embeddings:
            self._embeddings[model_name] = HuggingFaceEmbeddings(model_name=model_name)

        return self._embeddings[model_name]
