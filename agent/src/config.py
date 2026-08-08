from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"  # agent/.env

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )
    or_api_key: str = "test"
    openai_api_key: str = ""
    hf_api_key: str = ""
    chunk_size: int = 512
    chunk_overlap: int = 50
    embed_batch_size: int = 8
    max_file_size : int = 10 * 1024 * 1024  # 10 MB
    text_embedding : str = "BAAI/bge-small-en-v1.5"
    coll_name : str = "collection"
    chroma_port : int = 8000
    top_k_s: int = 5
    top_k_m: int = 8
    hnsw : dict ={
        "space": "cosine",
        "M": 16,
        "construction_ef": 100,
        "search_ef": 50
    }
    sync_delete: bool = True
    max_tokens: int = 2048
    temperature: float = 0


configs= AppConfig()