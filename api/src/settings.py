from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Embeddings
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Chroma
    chroma_collection_name: str = "chroma_collection"
    chroma_persist_directory: str = "chroma_db"
