from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings

from src.settings import Settings

class EmbeddingsService:
    """Serviço de geração de embeddings com cache em memória.

    Carrega modelos HuggingFace sob demanda e os mantém em cache para
    evitar recarregamentos desnecessários durante o ciclo de vida da aplicação.

    Attributes:
        _settings (Settings): Configurações com o nome do modelo padrão.
        _embeddings (dict[str, Embeddings]): Cache de modelos já carregados.
    """

    def __init__(self, settings: Settings):
        """Inicializa o serviço com as configurações da aplicação.

        Args:
            settings (Settings): Configurações contendo ``embedding_model_name``.
        """
        self._settings = settings
        self._embeddings: dict[str, Embeddings] = {}

    def get_embeddings(self, model_name: str | None = None) -> Embeddings:
        """Retorna a função de embedding para o modelo especificado.

        Se ``model_name`` não for informado, usa o modelo padrão definido em
        ``settings.embedding_model_name``. Modelos já carregados são reutilizados
        do cache interno.

        Args:
            model_name (str | None): Nome do modelo HuggingFace. Se ``None``,
                usa o modelo padrão das configurações.

        Returns:
            Embeddings: Instância de ``HuggingFaceEmbeddings`` pronta para uso.
        """
        if model_name is None:
            model_name = self._settings.embedding_model_name

        if model_name not in self._embeddings:
            self._embeddings[model_name] = HuggingFaceEmbeddings(model_name=model_name)

        return self._embeddings[model_name]
