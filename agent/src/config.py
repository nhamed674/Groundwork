from pydantic_settings import BaseSettings

class AppConfig (BaseSettings):
    # Define configuration variables here
    chunk_size: int = 512
    chunk_overlap: int = 50
    max_file_size = 10 * 1024 * 1024  # 10 MB
    text_embedding= "text-embedding-3-small"
    coll_name: str = "collection"
    hnsw={
        "space": "cosine",
        "M": 16,
        "construction_ef": 100,
        "search_ef": 50
    }

configs= AppConfig()