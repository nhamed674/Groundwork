import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from config import configs
import datetime

hnsw=configs.hnsw

def get_vector_store():
    chroma_client = chromadb.HttpClient(port=8000)  # Connect to the Chroma server
    collection = chroma_client.get_or_create_collection(
        name=configs.coll_name,
        metadata={
        "created_at": datetime.datetime.now().isoformat(),
        "hnsw:space": hnsw["space"],
        "hnsw:M": hnsw["M"],
        "hnsw:construction_ef": hnsw["construction_ef"],
        "hnsw:search_ef": hnsw["search_ef"],
        }
        )
    vector_store = ChromaVectorStore(chroma_collection=collection, embedding_dim=1536)
    return vector_store
