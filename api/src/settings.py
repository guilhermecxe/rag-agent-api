from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configurações globais da aplicação carregadas via variáveis de ambiente.
    """

    # Embeddings
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Chroma
    chroma_collection_name: str = "chroma_collection"
    chroma_persist_directory: str = "data/chroma_db"

    # Agent
    rag_agent_default_model: str = "openai:gpt-4o-mini"
    search_documents_limit: int = 5
