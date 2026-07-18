# Document Intelligence Agent Platform — Enterprise-Style Build Guide

A learning project that uses Terraform, Kubernetes, TypeScript, LangChain, LangGraph, LlamaIndex, AWS, and MLflow — built the way an engineering team at a real company would build it, not just the way that gets a demo working.

The gap between "it works on my machine" and "it works the way a company would ship it" isn't the tech stack — it's a set of habits around structure, review, environments, and safety nets. This guide walks through both at once.

---

## 0. How to use this guide

Each phase below has two parts:
- **Build** — what you're actually implementing
- **Enterprise practice** — the habit a real team would layer on top, and why

Do the Build steps in order. Adopt the Enterprise practices as you go — don't bolt them on at the end. Retrofitting CI, tests, or IaC state management onto a finished project is exactly the pain these practices exist to avoid.

---

## 1. Prerequisites

Install once, up front:

| Tool | Purpose |
|---|---|
| Node.js 20+, pnpm | Frontend, TypeScript tooling |
| Python 3.11+, uv or poetry | Agent backend, dependency locking |
| Docker + Docker Compose | Containers, local MLflow |
| kind | Local Kubernetes |
| kubectl | Talk to any Kubernetes cluster |
| Terraform CLI + tflocal | Infrastructure as code, local AWS emulation |
| LocalStack | Local AWS emulation |
| AWS CLI | Talk to real AWS (only needed for the final phase) |
| gh (GitHub CLI), git | Version control, PRs from the terminal |
| pre-commit | Git hook management |

**Enterprise practice:** teams pin exact versions in a `.tool-versions` (asdf) or `mise.toml` file, checked into the repo. "Works on my machine" is a version-drift problem 90% of the time — pinning kills that category of bug entirely.

---

## 2. Repository structure

Enterprises almost always use **one repo per deployable unit's logical boundary**, but for a project this size, a single monorepo with clear top-level separation is standard and easier to learn from:

```
project-root/
  .github/
    workflows/            # CI/CD pipelines
    CODEOWNERS
    pull_request_template.md
  agent/                  # Python: LlamaIndex + LangChain + LangGraph + FastAPI
    src/
      graph/              # LangGraph nodes and edges
      retrieval/          # LlamaIndex ingestion + query
      api/                # FastAPI routes
      config.py           # validated settings (pydantic-settings)
    tests/
      unit/
      integration/
    pyproject.toml
    Dockerfile
  frontend/               # TypeScript: Next.js chat UI
    src/
      app/
      features/
      components/
      lib/
    tests/
    package.json
    Dockerfile
  infra/
    modules/              # reusable Terraform modules: vpc, eks, s3, rds, ecr, iam
    envs/
      local/              # LocalStack tfvars + backend config
      staging/
      prod/
    README.md             # how to plan/apply per environment
  k8s/
    base/                 # shared Kustomize base manifests
    overlays/
      kind/
      staging/
      prod/
  mlflow/
    docker-compose.yml    # local MLflow (SQLite backend)
  docs/
    architecture/         # ADRs — see section 11
    runbooks/
  .pre-commit-config.yaml
  .env.example
```

**Enterprise practice:** the `envs/` split under `infra/` and `overlays/` split under `k8s/` is the actual enterprise pattern for environment promotion — the same modules and base manifests get reused across dev, staging, and prod, with only the variable values changing. If you find yourself copy-pasting a whole Terraform file to make a "prod version," that's the smell this structure prevents.

---

## 3. Git workflow

**Build:**
- `main` is always deployable. Nobody commits to it directly.
- Every change is a branch (`feature/langgraph-router`, `fix/mlflow-logging`) merged via pull request.
- Use **Conventional Commits**: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:` — this is what lets you auto-generate changelogs later and makes `git log` skimmable.

**Enterprise practice:**
- A `CODEOWNERS` file maps folders to reviewers (even if that's just you today — it's the mechanism teams use to route review automatically).
- A PR template forces you to state: what changed, why, how you tested it, and any rollback plan. Writing this before you open the PR catches half your own bugs.
- Branch protection: require at least one approval and passing CI before merge. On a solo project, "approval" can be a second look the next day with fresh eyes — the discipline matters more than the headcount.

---

## 4. Phase-by-phase build

### Phase 0 — Scaffolding (1–2 days)
**Build:** create the repo structure above, add `.env.example`, `.pre-commit-config.yaml` (ruff/black for Python, eslint/prettier for TS), and a root `README.md` stating what this project is and how to run it locally.

**Enterprise practice:** the README's first section is always "how do I run this in under 5 minutes." If a new hire (or future-you in six months) can't get a local environment running from the README alone, the README has failed its one job.

### Phase 1 — Agent core (1–2 weeks)
**Build:** LlamaIndex ingestion → LangChain RAG chain → LangGraph stateful router (simple lookup / multi-hop / clarify), returning cited answers.

**Enterprise practice:**
- Config (model name, chunk size, top-k) lives in `agent/src/config.py` validated with `pydantic-settings`, never hardcoded inline — this is what makes Phase 2's experiment sweeps possible without editing code.
- Write unit tests for the router's decision logic in isolation (mock the LLM call) before writing integration tests that hit a real model. Enterprises test the cheap, deterministic thing first.

### Phase 2 — Experiment tracking (3–5 days)
**Build:** log every agent run to MLflow — params, latency, a faithfulness score — and register your best config.

**Enterprise practice:** treat your MLflow "production" model registry stage as a real promotion gate — nothing gets marked `Production` without a documented reason (an MLflow tag or linked doc) for why this config beat the alternatives. This is the paper trail a team would want before trusting a config with real traffic.

### Phase 3 — API + frontend (1 week)
**Build:** FastAPI streaming endpoint, Next.js/TypeScript chat UI with citations and the agent-trace panel (see the earlier frontend structure discussion — `features/chat/`, `features/agent-trace/`).

**Enterprise practice:** the frontend never calls the agent directly with hardcoded URLs — all endpoints come from validated env vars (`lib/env.ts`), so the exact same build can point at local, staging, or prod just by swapping environment config, never by editing code.

### Phase 4 — Containerize + local Kubernetes (3–5 days)
**Build:** Dockerfiles for both services, `kind` cluster, Deployment/Service/Ingress manifests, HPA on the backend, MLflow as a pod.

**Enterprise practice:**
- Multi-stage Dockerfiles (build stage + slim runtime stage) — smaller images, smaller attack surface, faster deploys.
- Resource `requests`/`limits` on every container from day one. "It works" without limits is how one runaway pod takes down a shared cluster.
- Use Kustomize (the `base/` + `overlays/` split above) instead of maintaining near-duplicate YAML per environment.

### Phase 5 — Terraform against LocalStack (1 week)
**Build:** modules for S3, RDS/DynamoDB, ECR, IAM, validated with `tflocal` before touching real AWS.

**Enterprise practice:** this is where **remote state** and **state locking** get introduced, even against LocalStack, so the habit is already built before it matters for real: an S3 backend (or LocalStack's emulation of one) with DynamoDB-based locking, so two people (or two CI runs) can never `apply` at the same time and corrupt state. Also: `terraform fmt` and `terraform validate` as pre-commit hooks, and never editing `.tfstate` by hand.

### Phase 6 — Real AWS, one deliberate pass (a few hours)
**Build:** point Terraform at real AWS, add the EKS module, apply, deploy, verify, `terraform destroy` same day.

**Enterprise practice:** this is the only phase with real IAM stakes — every role you create should follow least-privilege (scope the EKS node role and any IRSA roles to only what's needed, not `*`). Tag every resource (`project`, `owner`, `environment`) — this is how real orgs do cost allocation and is also just good practice for finding your own orphaned resources before they quietly bill you.

---

## 5. CI/CD pipeline

**Build:** a GitHub Actions workflow with these stages, gating every PR:
1. Lint + type-check (both Python and TypeScript)
2. Unit tests
3. Build Docker images
4. `terraform fmt -check` + `terraform validate` (and `terraform plan` against LocalStack in CI, not real AWS)
5. On merge to `main`: push images to ECR, apply Terraform to staging, run integration tests against staging

**Enterprise practice:** CI never runs `terraform apply` against production automatically without a manual approval gate (GitHub Environments support this natively — a named "production" environment can require a specific reviewer to click approve). This one rule is the difference between "a bad PR breaks staging" and "a bad PR takes down prod at 2am."

---

## 6. Environment strategy

Three environments, same artifacts promoted through them:

| Environment | Purpose | Infra |
|---|---|---|
| local | Individual development | kind + LocalStack, $0 |
| staging | Integration testing, demos | Small real AWS footprint, always-on but minimal (or spun up on demand) |
| prod | The real thing | Only exists once you'd actually ship this to users |

**Enterprise practice:** the same Docker image gets built once and promoted (local → staging → prod) rather than rebuilt per environment — this is what guarantees "it worked in staging" actually means something. Only environment *configuration* (env vars, secrets, replica counts) changes between environments, never the code.

---

## 7. Secrets and configuration

**Build:** `.env.example` lists every required variable with placeholder values — never real ones. Real secrets never touch git, ever, including in commit history.

**Enterprise practice:**
- Local: `.env` file, gitignored.
- Real AWS: **AWS Secrets Manager** or **SSM Parameter Store**, referenced by ARN in Terraform/Kubernetes, never pasted into manifests.
- A `git-secrets` or `gitleaks` pre-commit hook that blocks commits containing anything that looks like an API key. Assume a secret will eventually almost get committed — the hook is the safety net, not a moral judgment on your carefulness.

---

## 8. Testing strategy

| Layer | What it covers | Speed |
|---|---|---|
| Unit | LangGraph node logic, retrieval scoring, React components in isolation | Fast, runs on every save |
| Integration | Full agent request against a real (cheap) LLM + real vector store | Slower, runs in CI |
| End-to-end | Frontend → backend → agent, in a kind cluster | Slowest, runs pre-merge or nightly |

**Enterprise practice:** the test pyramid shape matters — lots of unit tests, fewer integration tests, a handful of e2e tests. A codebase with the pyramid inverted (mostly e2e tests) is famously slow to run and painful to debug when something breaks, because a failure could be anywhere in the stack.

---

## 9. Observability

**Build:** structured JSON logging (not `print()`/`console.log`) in both the FastAPI backend and the Next.js server, with a request ID that flows through the LangGraph execution so you can trace one user's request through every node.

**Enterprise practice:** the three pillars — **logs** (what happened), **metrics** (aggregate numbers: request latency, token usage, error rate — exposed for Prometheus/CloudWatch), and **traces** (the path one request took, ideally via OpenTelemetry). You don't need all three from day one, but structure your logging so adding metrics and tracing later doesn't require a rewrite — that mostly means: always include a request ID, always log in structured (JSON) format, never string-interpolate log messages.

---

## 10. Security basics

- **Least privilege IAM** everywhere — the EKS node role, any IRSA role, your own AWS CLI credentials should only have what they need.
- **Dependency scanning** — `pip-audit` / `npm audit` (or Dependabot) in CI, so a vulnerable transitive dependency doesn't sit unnoticed for months.
- **No secrets in images** — never `COPY .env` into a Docker image; inject at runtime via Kubernetes Secrets or env vars.
- **Network policy** — even a basic Kubernetes NetworkPolicy restricting which pods can talk to which is standard once you're past "everything in one namespace, trust everything."

---

## 11. Documentation practices

**Build:** two lightweight but real artifacts, kept in `docs/`:
- **ADRs (Architecture Decision Records)** — one short markdown file per significant decision ("why LangGraph over a plain LangChain chain," "why EKS over ECS"), stating the context, the decision, and the tradeoffs considered. Future-you (or a teammate) should never have to guess why something is the way it is.
- **Runbooks** — "MLflow tracking server is down, here's how to check it," "agent is returning empty answers, here's the debug checklist." Written *before* you need them, ideally right after you first debug something the hard way.

**Enterprise practice:** ADRs are almost always underused by beginners and almost always the thing senior engineers wish junior engineers wrote more of. They cost 10 minutes and save hours of "wait, why did we do it this way?" months later.

---

## 12. Cost governance

- Tag every AWS resource with `project`, `owner`, `environment` via Terraform (`default_tags` on the AWS provider block covers this in one place).
- Set a **billing alarm** in AWS Budgets before your first real `terraform apply` — a $10 threshold alert costs nothing to set up and catches a forgotten `destroy` before it becomes a real bill.
- Always `terraform destroy` real AWS resources the same session you created them, unless you have an explicit reason to keep them running.

---

## 13. Definition of done — milestone checklist

Use this to know when a phase is actually complete, not just "seems to work":

- [ ] Code is behind a PR, reviewed (even self-reviewed the next day), and merged — not committed straight to `main`
- [ ] Tests exist for the new logic and pass in CI
- [ ] Config is externalized (no hardcoded secrets, URLs, or magic numbers)
- [ ] Resources are tagged (if AWS) and have limits set (if Kubernetes)
- [ ] A README or ADR update explains what changed and why
- [ ] If it touches real AWS: destroyed or downsized before you walk away

---

## 14. Glossary

| Term | Meaning |
|---|---|
| IaC | Infrastructure as Code — infra defined in files (Terraform), not clicked in a console |
| IRSA | IAM Roles for Service Accounts — how a Kubernetes pod gets scoped AWS permissions |
| ADR | Architecture Decision Record — a short doc capturing why a technical decision was made |
| Trunk-based development | Everyone branches off and merges back into one main branch frequently, avoiding long-lived branches |
| Least privilege | Granting only the exact permissions needed, nothing broader "just in case" |
| Promotion | Moving the same tested artifact through environments (staging → prod) rather than rebuilding per environment |

---

### Suggested pacing

5–7 weeks part-time, 2–3 weeks full-time — same as the original plan, with the enterprise practices woven in per phase rather than tacked on afterward. The goal isn't to gold-plate a learning project; it's to build the muscle memory for habits that are expensive to learn for the first time on a production system with real users watching.
