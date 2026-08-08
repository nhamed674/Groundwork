import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from config import configs
import datetime

hnsw=configs.hnsw

def get_chroma_collection():
    chroma_client = chromadb.HttpClient(port=configs.chroma_port)  # Connect to the Chroma server
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
    return collection

def get_vector_store():
    collection = get_chroma_collection()
    vector_store = ChromaVectorStore(chroma_collection=collection, embedding_dim=384)
    return vector_store

def delete_vector_store():
    chroma_client = chromadb.HttpClient(port=configs.chroma_port)  # Connect to the Chroma server
    chroma_client.delete_collection(name=configs.coll_name)


def document_exists(document_id: str) -> bool:
    collection = get_chroma_collection()
    results = collection.get(
        where={"source_document_id": document_id}
    )

    return bool(results["ids"])


def get_document_hash(document_id: str) -> str | None:
    collection = get_chroma_collection()
    results = collection.get(
        where={"source_document_id": document_id},
        include=["metadatas"]
    )

    metadatas = results["metadatas"]

    if not metadatas:
        return None

    hashes = {
        metadata.get("file_hash")
        for metadata in metadatas
        if metadata is not None
    }

    if len(hashes) > 1:
        raise ValueError(
            f"Inconsistent content hashes for document: {document_id}"
        )

    return hashes.pop()

def delete_document(document_id: str):
    collection = get_chroma_collection()
    collection.delete(
        where={"source_document_id": document_id}
    )

def load_documents_from_vector_store():
    vector_store = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = storage_context.get_index()
    return index.as_retriever().retrieve_all()

def get_all_document_ids() -> tuple[str]:
    collection = get_chroma_collection()
    results = collection.get(include=["metadatas"])
    metadatas = results.get("metadatas") or []
    document_ids = {
        metadata["source_document_id"]
        for metadata in metadatas
        if metadata is not None and "source_document_id" in metadata
    }

    return tuple(document_ids)