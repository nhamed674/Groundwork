# Groundwork — What to implement next

Source of truth for remaining work, branching, and TypeScript OpenAPI types.
Agent core (RAG + LangGraph + FastAPI `/chat` + `/health`) is done.

---

## Done

- Config, ingest, Chroma, incremental sync
- Retriever, Pydantic models, LangChain prompt/chain
- Citation validation (verified cites + warning)
- Linear LangGraph: retrieve → generate → validate
- FastAPI: `POST /chat`, `GET /health`, Swagger

**Not done vs full Stage 1 DoD:** query router, multi-hop, clarify path, conversation memory, unit tests, CLI.

---

## Remaining (in order)

### Now — Frontend + typed API client (Stage 3)

1. CORS on FastAPI for `http://localhost:3000`
2. Scaffold Next.js in `frontend/` (`features/chat/`, `features/agent-trace/`)
3. **Generate TS types from OpenAPI** (see below) — do this before writing the client by hand
4. `lib/env.ts` — zod-validate `NEXT_PUBLIC_API_URL`
5. `lib/api-client.ts` — only HTTP layer; use generated types; no `fetch` in components
6. Chat UI: question → answer + citations + `citation_warning`
7. Trace panel: show `route_taken` (`rag` for now)
8. Sync JSON first; streaming later

### Then

| Stage | Build |
|-------|--------|
| 2 | MLflow tracking of agent runs |
| 4 | Dockerfiles + kind/K8s |
| 5 | Terraform + LocalStack |
| 6 | CI: lint, `tsc`, tests, tf validate |
| 7 | One real AWS apply + destroy |
| 8 | Logs/metrics (stretch) |

Optional later (still Stage 1): LangGraph router, memory, tests.

---

## Generate TS types from FastAPI OpenAPI

Keep frontend types in sync with `ChatRequest` / `AgentResponse` / `Citation`. Do not hand-copy Python models.

**Backend (small cleanups so the schema is JSON-friendly):**

- CORS middleware
- Prefer `invalid_citations: list[int]` over `set[int]` (OpenAPI/JSON)
- Keep `/openapi.json` stable (`title`, route models)

**Frontend:**

```bash
cd frontend
pnpm add -D openapi-typescript
```

With the API running:

```bash
pnpm exec openapi-typescript http://127.0.0.1:8008/openapi.json -o src/lib/api-types.ts
```

Add a script in `frontend/package.json`, e.g. `"gen:api": "openapi-typescript http://127.0.0.1:8008/openapi.json -o src/lib/api-types.ts"`.

Use `components["schemas"]` from `api-types.ts` in `api-client.ts`. Regenerate after any FastAPI schema change.

---

## Next steps (do these now)

1. Commit current agent/API work on `feature/agent-api` (or similar), open a PR into `main`.
2. Enable CORS on the FastAPI app.
3. Create `feature/frontend-chat` from updated `main`.
4. Scaffold Next.js in `frontend/`.
5. Run the API, generate `src/lib/api-types.ts`.
6. Build `env.ts` + `api-client.ts` + a minimal chat page.
7. Manually test: browser → `/chat` → cited answer.

Do not start Docker/K8s/Terraform until the chat UI works.

---

## Branching

- `main` is always deployable. No direct commits to `main`.
- One feature branch per stage (or per vertical slice). Merge with a PR.
- Names: `feature/<area>`, `fix/<area>`. Conventional commits: `feat:`, `fix:`, `chore:`.
- After merge, delete the feature branch. Next branch is cut from latest `main`.

```text
main
  └── feature/agent-api          # ingest → graph → FastAPI (current work)
        └── merge to main
  └── feature/frontend-chat      # Next.js + OpenAPI types + chat UI
        └── merge to main
  └── feature/mlflow-tracking
        └── merge to main
  └── feature/docker-kind
        └── merge to main
  └── feature/terraform-localstack
        └── merge to main
  └── feature/ci-cd
        └── merge to main
  └── feature/aws-deploy         # one apply + destroy; merge docs, not a live cluster
        └── merge to main
```

Optional extras (merge only if you build them):

- `feature/langgraph-router` — classify / multi-hop / clarify
- `feature/streaming-chat` — SSE + streamed UI
- `feature/observability` — Stage 8

### Branches to merge by the end

These are the branches that should land on `main` for the full learning project:

1. `feature/agent-api`
2. `feature/frontend-chat` (includes OpenAPI TS codegen)
3. `feature/mlflow-tracking`
4. `feature/docker-kind`
5. `feature/terraform-localstack`
6. `feature/ci-cd`
7. `feature/aws-deploy`

Do not keep them all open in parallel. Finish and merge each before starting the next, except `frontend-chat` may follow immediately after `agent-api`.
