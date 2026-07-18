# Groundwork — Project Stages

Nine stages, each with a clear goal, what you need before starting, what you actually build, and how you know you're done. Stages 0–5 cost nothing but LLM API calls. Stage 7 is the only one that touches real money.

---

## Stage 0 — Environment & Repo Setup

**Goal:** a working skeleton repo and every tool installed, so no later stage is blocked on tooling.

**Requirements:**
- Node.js 20+, pnpm, Python 3.11+, uv or poetry, Docker Desktop, kind, kubectl, Terraform CLI, LocalStack, AWS CLI, git, gh CLI
- No prior knowledge required — this is pure setup

**Tasks:**
1. Create the repo with the folder structure (`agent/`, `frontend/`, `infra/`, `k8s/`, `mlflow/`, `docs/`)
2. Add `.env.example`, `.gitignore`, `.pre-commit-config.yaml` (ruff/black for Python, eslint/prettier for TS)
3. Add a root `README.md` stub (fill in properly once something actually runs)
4. Verify every tool installed with a version check (`docker --version`, `kind version`, `terraform -version`, etc.)
5. Set up branch protection on `main` (require PR + passing CI, even solo)

**Definition of done:**
- [ ] Repo exists with the full folder skeleton, even if most folders are empty
- [ ] `pre-commit install` runs clean
- [ ] Every tool from the prerequisites table responds to a version check
- [ ] First commit pushed, `main` branch protected

**Estimated time:** half a day

---

## Stage 1 — Agent Core (RAG + LangGraph)

**Goal:** a CLI tool that answers a question about your documents with a cited source, choosing its reasoning path (simple lookup / multi-hop / clarify) automatically.

**Requirements:**
- Stage 0 complete
- An LLM API key (OpenAI, Anthropic, or similar) with a small budget ($5–10)
- A document set to test against (20–50 files is plenty — markdown, PDFs, or text)
- Working knowledge of Python; no prior LangChain/LangGraph/LlamaIndex experience needed

**Tasks:**
1. Set up `agent/pyproject.toml`, install LlamaIndex, LangChain, LangGraph
2. Write an ingestion script: load documents → chunk → embed → build a vector index (start with an in-memory or local Chroma store)
3. Build a basic LangChain RAG chain (retriever → prompt → LLM) — get one query working end to end before anything fancier
4. Rebuild the orchestration as a LangGraph graph with at least three nodes: `classify_query`, `simple_retrieval`, `multi_hop_research`, plus a `clarify` path for ambiguous questions
5. Add conversation memory so follow-up questions have context
6. Wire citations into every answer — no answer without a traceable source
7. Write unit tests for the router's classification logic with the LLM call mocked

**Definition of done:**
- [ ] `python -m agent.cli "your question"` returns an answer with at least one citation
- [ ] The three example queries from the earlier walkthrough (simple lookup, multi-hop, ambiguous) each take a visibly different path through the graph
- [ ] Router classification has unit tests that don't require a live LLM call
- [ ] `config.py` externalizes model name, chunk size, and top-k — nothing hardcoded inline

**Estimated time:** 1–2 weeks

---

## Stage 2 — Experiment Tracking (MLflow)

**Goal:** every agent run logged and comparable, with a "best config" you can point to and justify.

**Requirements:**
- Stage 1 complete
- Docker (for the local MLflow container)

**Tasks:**
1. Add `mlflow/docker-compose.yml` — MLflow server with a SQLite backend and local artifact store
2. Wrap every agent invocation in an MLflow run, logging: prompt template version, chunk size, top-k, model name, latency, and a quality score (a simple LLM-as-judge faithfulness check, or `ragas` if you want more rigor)
3. Run at least three config sweeps (vary chunk size and top-k independently) against the same set of test questions
4. Compare runs in the MLflow UI, pick a winner, and register it as a model version tagged `Production` with a one-line reason why

**Definition of done:**
- [ ] `docker compose up` in `mlflow/` brings up a working MLflow UI at `localhost:5000`
- [ ] At least 10 tracked runs visible in the UI
- [ ] One config registered as `Production` with a documented reason (an MLflow tag or a linked note in `docs/`)

**Estimated time:** 3–5 days

---

## Stage 3 — API + Frontend

**Goal:** a real chat web app — not a CLI — with streamed answers, citations, and a visible reasoning trace.

**Requirements:**
- Stage 1 complete (Stage 2 not strictly required, but doing it first means you're wrapping a *tracked* agent, not an untracked one)
- Basic TypeScript/React familiarity, or willingness to learn as you go

**Tasks:**
1. Wrap the LangGraph agent in FastAPI with a streaming endpoint (SSE or WebSocket)
2. Scaffold the Next.js frontend using the feature-folder structure (`features/chat/`, `features/agent-trace/`)
3. Build the chat UI: message list, streamed token rendering, citation display
4. Build the agent-trace panel showing which graph node handled the current query
5. Add a typed API client layer (`lib/api-client.ts`) — no raw `fetch()` calls inside components
6. Validate all environment variables at startup with a schema (zod) — fail fast on a missing backend URL, don't fail silently at request time

**Definition of done:**
- [ ] `pnpm dev` + backend running locally lets you ask a question in the browser and see a streamed, cited answer
- [ ] The trace panel updates to reflect the actual graph path taken
- [ ] No component calls `fetch` directly; all requests go through the typed client
- [ ] Missing env vars cause a clear startup error, not a silent runtime failure

**Estimated time:** 1 week

---

## Stage 4 — Containerize + Local Kubernetes

**Goal:** the full stack (frontend, backend, MLflow) running in a local Kubernetes cluster, not just `pnpm dev` / `uvicorn` processes on your machine.

**Requirements:**
- Stages 1–3 complete
- kind and kubectl installed and working
- Basic familiarity with YAML

**Tasks:**
1. Write multi-stage Dockerfiles for the agent backend and the frontend (build stage + slim runtime stage)
2. Create a `kind` cluster, install the nginx ingress addon
3. Write Kubernetes manifests using the base + overlay pattern: Deployment, Service, and Ingress for each app, resource `requests`/`limits` on every container
4. Add a HorizontalPodAutoscaler on the backend and load-test locally to confirm it actually scales
5. Deploy MLflow as a pod backed by a PersistentVolumeClaim

**Definition of done:**
- [ ] `kubectl apply -k k8s/overlays/kind` brings up the full stack
- [ ] The app is reachable through the Ingress, not just `port-forward`
- [ ] Every container has resource requests and limits set
- [ ] A basic load test visibly triggers the HPA to add a pod

**Estimated time:** 3–5 days

---

## Stage 5 — Infrastructure as Code (Terraform + LocalStack)

**Goal:** Terraform modules for every AWS resource this project needs, fully validated against LocalStack before real AWS is ever touched.

**Requirements:**
- Stage 4 complete (you need to know what the app needs infrastructure-wise before you can provision it)
- LocalStack running, `tflocal` installed
- No prior Terraform experience required, but comfort reading HCL syntax helps

**Tasks:**
1. Write modules for: S3 (documents + MLflow artifacts), RDS or DynamoDB (chat history / MLflow backend), ECR (image repos), IAM (roles and policies)
2. Set up a remote state backend (S3 + DynamoDB lock table, emulated via LocalStack) — even though it's local, build the habit now
3. `tflocal apply` repeatedly, iterating until `terraform plan` is clean and every resource appears correctly in LocalStack
4. Add `terraform fmt` and `terraform validate` as pre-commit hooks
5. Explicitly skip EKS here — LocalStack's free tier doesn't cover it; that's Stage 7

**Definition of done:**
- [ ] `tflocal apply` in `infra/envs/local` succeeds cleanly from a fresh state
- [ ] State is remote (not local `.tfstate` file) with locking configured
- [ ] `terraform fmt -check` and `terraform validate` pass and are wired into pre-commit
- [ ] Every resource has `project`/`owner`/`environment` tags set via `default_tags`

**Estimated time:** 1 week

---

## Stage 6 — CI/CD Pipeline

**Goal:** every PR automatically linted, tested, and validated — nothing merges to `main` on faith.

**Requirements:**
- Stages 1–5 complete
- A GitHub repo (or equivalent) with Actions enabled

**Tasks:**
1. Write a workflow that runs on every PR: lint + type-check (Python and TypeScript), unit tests, Docker image builds, `terraform fmt -check` + `validate` + `plan` against LocalStack
2. Write a second workflow that runs on merge to `main`: push images to ECR (once Stage 7 exists), run integration tests
3. Set up a GitHub Environment named `production` requiring manual approval before any workflow can apply Terraform against real AWS
4. Add a PR template and a `CODEOWNERS` file

**Definition of done:**
- [ ] Opening a PR triggers all checks automatically and blocks merge if any fail
- [ ] A deliberately broken test or a deliberately malformed Terraform file fails CI as expected
- [ ] Applying to real AWS requires a manual approval step, verified by testing it (approve/reject) before Stage 7 begins

**Estimated time:** 3–5 days

---

## Stage 7 — Real AWS, One Deliberate Pass

**Goal:** confirm the entire stack actually deploys to real AWS, and capture what's different from the local/LocalStack version — then tear it all down the same day.

**Requirements:**
- Stages 1–6 complete
- A real AWS account with billing set up
- A billing alarm configured in AWS Budgets **before** the first `apply`
- Set aside a few uninterrupted hours — this stage should not be left half-finished overnight

**Tasks:**
1. Add the EKS module to Terraform (the one thing untestable against LocalStack)
2. Point Terraform at real AWS (swap backend/provider config to `infra/envs/prod`)
3. `terraform apply` — provisions EKS, S3, RDS/DynamoDB, ECR, IAM roles including IRSA
4. Push Docker images to the real ECR repo
5. `kubectl apply` the same manifests used against `kind`, adjusting only the overlay (load balancer controller, storage class, IRSA annotations)
6. Verify the app works end to end on a real URL
7. Write down every difference you hit versus the LocalStack/kind version — this becomes a `docs/` note
8. `terraform destroy` before ending the session

**Definition of done:**
- [ ] The app is reachable and fully functional on real AWS infrastructure
- [ ] Every IAM role follows least privilege (no `*` actions/resources without a documented reason)
- [ ] A short write-up exists in `docs/` capturing what differed from local
- [ ] `terraform destroy` has been run and confirmed (check the AWS console, not just the CLI output)
- [ ] Total AWS spend for the session is under ~$20

**Estimated time:** a few hours, one weekend

---

## Stage 8 — Observability & Hardening (stretch goal)

**Goal:** the habits that make a system debuggable and safe once it has real users, even if this project never actually gets real users.

**Requirements:**
- Stage 7 complete (or at least Stage 6, if you're doing this against the local stack only)

**Tasks:**
1. Add structured JSON logging to both the backend and frontend server, with a request ID that flows through the LangGraph execution
2. Expose basic metrics (request latency, token usage, error rate) for Prometheus or CloudWatch
3. Add a Kubernetes NetworkPolicy restricting which pods can talk to which
4. Add `pip-audit` / `npm audit` to CI for dependency scanning
5. Write two runbooks in `docs/runbooks/`: "MLflow is down," "agent returns empty answers" — write these from an actual debugging session, not hypothetically

**Definition of done:**
- [ ] A single request can be traced end to end through logs using its request ID
- [ ] At least one metric is visible in a dashboard (even a simple one)
- [ ] Dependency scanning runs in CI and would catch a known-vulnerable package
- [ ] Two runbooks exist and were tested by deliberately breaking the thing they describe

**Estimated time:** 3–5 days

---

## At a glance

| Stage | Focus | Cost | Time |
|---|---|---|---|
| 0 | Setup | $0 | 0.5 day |
| 1 | Agent core | $ (LLM calls) | 1–2 weeks |
| 2 | Experiment tracking | $0 | 3–5 days |
| 3 | API + frontend | $ (LLM calls) | 1 week |
| 4 | Local Kubernetes | $0 | 3–5 days |
| 5 | Terraform + LocalStack | $0 | 1 week |
| 6 | CI/CD | $0 | 3–5 days |
| 7 | Real AWS | ~$10–20, one session | few hours |
| 8 | Observability (stretch) | $0 | 3–5 days |
