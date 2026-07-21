**Dependencies Manager:**
- uv (uv sync)
retrieval/

ingest.py
──────────

- [x] Load files

- [x] Validate files

- [x] Add metadata

- [x] Chunk documents

- [x] Build embeddings

- [ ] Create/update index (changing files not implemented yet needs chromadb)


vector_store.py

────────────────
- [x] Create Chroma client
- [x] Open collection
- [x] Return vector store
- [x] Hide database-specific code

retriever.py
────────────
Load existing index
Search by query
Return top-k chunks
Nothing about FastAPI
Nothing about LangGraph