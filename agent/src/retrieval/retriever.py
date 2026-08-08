from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from retrieval.vector_store import get_vector_store
from config import configs
from generation.models import Chunk


class Retriever:

    def __init__(self):

        # Use the same embedding model as ingestion
        Settings.embed_model = HuggingFaceEmbedding(
            model_name=configs.text_embedding,
            embed_batch_size=16,
            device="cpu",
        )

        # Connect to existing Chroma vector store
        vector_store = get_vector_store()

        # Load existing index from Chroma
        self.index = VectorStoreIndex.from_vector_store(
            vector_store
        )

        self.top_k = configs.top_k_m

    def retrieve(
        self,
        query: str,
        top_k: int | None = None
    ):

        if top_k is None:
            top_k = self.top_k

        retriever = self.index.as_retriever(
            similarity_top_k=top_k
        )

        return retriever.retrieve(query)
    
    def retrieve_chunks(self,
                        query:str,
                        top_k: int | None = None
    ) -> list[Chunk]:
        chunks= []
        results = self.retrieve(query=query,top_k=top_k)
        for result in results:
            metadata = result.node.metadata
            title = metadata.get("title")
            doc_type = metadata.get("doc_type")
            source = title + doc_type
            text = result.get_content()
            source_path = metadata.get("file_path")
            score = result.get_score()
            chunks.append(Chunk(metadata=metadata, 
                                       text=text, 
                                       source_path=source_path, 
                                       score=score,
                                       source=source
                                       )
                        )
        return chunks

