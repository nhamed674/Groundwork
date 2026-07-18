# Groundwork

A document intelligence agent that answers questions over your own documents with cited sources — built and deployed the way a real engineering team would do it, from local dev to a real (briefly-running) AWS deployment.

**The name is a double meaning:** answers are *grounded* in cited source documents, not guesses. The project itself is about laying the *groundwork* — the infrastructure discipline (IaC, CI/CD, environments, observability) that separates a demo from something a team would trust.

---

## What it does

- Ingests a set of documents and answers questions about them, with inline citations back to the source
- Routes each question through a decision graph — simple lookup, multi-hop research, or "ask the user to clarify" — instead of one flat prompt
- Logs every run (config, latency, a quality score) so configurations can be compared and improved over time
- Streams responses to a chat UI, showing which step of the reasoning graph handled the question
- Runs entirely free on your laptop, and deploys to real AWS using the exact same code

## Tech stack

| Layer | Tool | Role |
|---|---|---|
| Retrieval | LlamaIndex | Document ingestion and vector search |
| Orchestration | LangChain + LangGraph | RAG chain and the stateful reasoning graph |
| Experiment tracking | MLflow | Logs and compares every agent run |
| Backend | FastAPI | Streams agent responses to the frontend |
| Frontend | TypeScript / Next.js | Chat UI with citations and a live reasoning trace |
| Infrastructure | Terraform | Provisions everything as code |
| Deployment | Kubernetes (kind locally, EKS in AWS) | Runs the containerized services |
| Cloud | AWS (via LocalStack for local dev) | S3, RDS, ECR, IAM |

## Architecture

```
TypeScript frontend → FastAPI backend → LangGraph router
                                              │
                                ┌─────────────┴──────────────┐
                                ▼                             ▼
                    LlamaIndex + LangChain              MLflow (logs every run)
                    (retrieves from your docs)
```

Full write-up of the architecture and the local-vs-AWS deployment split lives in [`docs/architecture/`](docs/architecture/).

## Quickstart (local, free)

Everything below runs on your machine with no AWS account and no cost.

```bash
# 1. clone and install
git clone <this-repo>
cd groundwork
cp .env.example .env          # fill in your LLM API key

# 2. start MLflow locally
cd mlflow && docker compose up -d && cd ..

# 3. install and run the agent backend
cd agent
uv sync                        # or: poetry install
uv run uvicorn src.api.main:app --reload
# backend now running at http://localhost:8000

# 4. install and run the frontend, in a new terminal
cd frontend
pnpm install
pnpm dev
# frontend now running at http://localhost:3000
```

Open `http://localhost:3000`, ask a question, and you should see a streamed answer with citations and a trace of which graph node handled it. MLflow's UI is at `http://localhost:5000`.

### Running the full stack in Kubernetes (still free)

```bash
kind create cluster --name groundwork
kubectl apply -k k8s/overlays/kind
kubectl port-forward svc/frontend 3000:3000
```

### Provisioning infrastructure locally (still free)

```bash
cd infra/envs/local
tflocal init
tflocal apply
```

This provisions S3, RDS/DynamoDB, ECR, and IAM against LocalStack, not real AWS — safe to run and destroy as many times as you want.

### Deploying to real AWS (costs money — see warning below)

```bash
cd infra/envs/prod
terraform init
terraform apply    # provisions a real EKS cluster + AWS resources
# ... deploy, verify ...
terraform destroy  # do this the same session
```

> **Cost warning:** a real EKS cluster + RDS + load balancer runs roughly $150–250/month if left running continuously. Only apply this against real AWS for a short, deliberate session, and `destroy` immediately after. A billing alarm is configured in `infra/modules/budget` — set it up before your first real `apply`.

## Repository structure

```
groundwork/
  agent/       Python: LlamaIndex + LangChain + LangGraph + FastAPI
  frontend/    TypeScript: Next.js chat UI
  infra/       Terraform modules and per-environment configs
  k8s/         Kubernetes manifests (base + kind/staging/prod overlays)
  mlflow/      Local MLflow via docker-compose
  docs/        Architecture decisions and runbooks
```

## Environments

| Environment | Infra | Cost |
|---|---|---|
| `local` | kind + LocalStack | $0 |
| `staging` | Small real AWS footprint | Minimal, spun up on demand |
| `prod` | Real EKS + managed AWS services | Real — see cost warning above |

The same Docker image is built once and promoted through these environments; only configuration changes between them.

## Contributing

- `main` is always deployable — work happens on branches, merged via PR
- Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`) for commit messages
- CI runs lint, type-check, unit tests, and `terraform plan` against LocalStack on every PR
- See [`docs/architecture/`](docs/architecture/) for ADRs before making a significant design change

## License

Add your license of choice here (MIT is a common default for learning/portfolio projects).
