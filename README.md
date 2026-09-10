# Groundwork

Groundwork answers questions about your own documents and backs every claim with citations from the source material.

Ask a question in the chat UI. The agent retrieves relevant passages from your document store, generates an answer grounded only in that context, and returns verified citations (source, page, snippet). Invalid or invented citation markers are dropped and flagged.

## Features

- **Document Q&A** over PDFs, Word files, slides, HTML, Markdown, and text
- **Cited answers** with validated references to retrieved chunks
- **Chat UI** (Next.js) showing the answer, sources, and which reasoning path was used
- **HTTP API** (`POST /chat`) for the same flow without the UI

## How it works

```
Documents → ingest & embed → ChromaDB
                                  ↓
Chat / API → retrieve → generate → validate citations → response
```

| Piece | Role |
|-------|------|
| LlamaIndex + ChromaDB | Ingestion, embeddings, vector search |
| LangChain + LangGraph | Prompting, generation, citation checks |
| FastAPI | `POST /chat`, `GET /health` |
| Next.js + TypeScript | Chat interface |

## Run locally

**API** (from `agent/`, with your keys in `agent/.env`):

```bash
uv sync
uv run uvicorn api.main:app --reload --app-dir src --port 8008
```

**UI** (from `frontend/`, with `NEXT_PUBLIC_API_URL=http://127.0.0.1:8008` in `.env.local`):

```bash
pnpm install
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000), ask a question, and inspect the answer and sources.
