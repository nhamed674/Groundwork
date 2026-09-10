# Groundwork

Ask questions over your own documents and get answers with citations.

Groundwork retrieves relevant passages from your files, answers only from that context, and returns verified sources (file, page, snippet). Fake citation markers are dropped.

## Stack

- **LlamaIndex + ChromaDB** — ingest, embed, search
- **LangChain + LangGraph** — generate and validate citations
- **FastAPI** — `POST /chat`
- **Next.js** — chat UI

## Run

API (`agent/`, keys in `agent/.env`):

```bash
uv sync
uv run uvicorn api.main:app --reload --app-dir src --port 8008
```

UI (`frontend/`, set `NEXT_PUBLIC_API_URL=http://127.0.0.1:8008` in `.env.local`):

```bash
pnpm install
pnpm dev
```

Open http://localhost:3000
