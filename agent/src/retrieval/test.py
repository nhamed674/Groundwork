from retrieval.retriever import Retriever
from . import vector_store
import time


# vector_store.delete_vector_store()
# collection = vector_store.get_chroma_collection()

# data = collection.get(include=["metadatas"])
# metadatas = data.get("metadatas") or []

# for nr, metadata in enumerate(metadatas):
#     print("#" * 20)
#     print(f"Document {nr + 1}:")
#     print("")
#     print(metadata)
#     print("")
#     print("#" * 20)
#     print("")
#     print("")

query = "Lung cancer"
retriever=Retriever()

start = time.perf_counter()

results = retriever.retrieve_chunks(query, top_k=5)

elapsed = time.perf_counter() - start

print("#"*50)
print(f"elapsed querry time: {elapsed}")
print("#"*50+"\n\n")

print(f"## Results for query '{query}':")
for i, result in enumerate(results):
    print(result)
    # print(f"-"*75)
    # print(f"Result {i+1}: \n\n{result.node.get_content()}")
    # print(f"Metadata: {result.node.metadata}")
    # print(f"Score: {result.get_score()}")
    # print(f"Node ID: {result.node.node_id}")
