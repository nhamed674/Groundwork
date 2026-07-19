# Stage 1 — Agent Core: Requirements Specification

This is the parameter sheet a stakeholder would hand you before Stage 1 starts — every value that would otherwise be a guess, specified concretely, with the reasoning behind it. Treat these as sane defaults to implement first and tune later against real evaluation data (Stage 2), not as permanent laws.

---

## 1. Document ingestion

| Parameter | Value | Rationale |
|---|---|---|
| Supported file types | `.md`, `.pdf`, `.txt`, `.docx` | Covers the common formats for internal docs without building a universal parser on day one |
| Max file size | 10 MB per file | Above this, ingestion time and memory use degrade fast; split larger files upstream instead |
| Encoding | UTF-8 enforced, reject/flag anything else | Silent mojibake in retrieved chunks is a debugging trap — fail loudly at ingestion, not at query time |
| Metadata captured per document | `source_path`, `title`, `last_modified`, `doc_type` | This is what makes citations meaningful — a citation with no source path is useless |

## 2. Chunking

| Parameter | Value | Rationale |
|---|---|---|
| **Chunk size** | **512 tokens** | The standard middle ground: small enough for precise retrieval, large enough to preserve paragraph-level context. Below ~256 tokens you fragment ideas mid-thought; above ~1024 you start retrieving noise alongside the answer. |
| **Chunk overlap** | **50 tokens (~10%)** | Prevents a fact from being split exactly at a chunk boundary and becoming unretrievable from either side. 10–15% overlap is the standard range; going much higher just duplicates storage and retrieval noise. |
| Chunking strategy | **Sentence-aware splitting** (LlamaIndex `SentenceSplitter`), not naive fixed-token cuts | Never cut mid-sentence — it produces chunks that read as garbled fragments and hurts both retrieval relevance and the LLM's ability to use the chunk correctly |
| Chunking unit for code/config files | Split by function/class boundary where possible, fall back to fixed-size | A 512-token window through a code file is far more useful when it doesn't sever a function in half |
| Table handling | Keep tables intact as a single chunk if under 1024 tokens; otherwise split by row-group with header repeated in each chunk | Splitting a table loses the header context that makes the numbers meaningful |

## 3. Embeddings

| Parameter | Value | Rationale |
|---|---|---|
| Embedding model | `text-embedding-3-small` (OpenAI) or an equivalent open model (`bge-small-en-v1.5`) if you want to avoid a second API dependency | Small embedding models are ~5x cheaper than large ones with a small (often under 2%) retrieval quality gap for most internal-document use cases — not worth the cost for a learning project |
| Embedding dimension | 1536 (OpenAI small) or 384 (bge-small) | Determined by model choice above; recorded here because it affects vector store index config |
| Batch size for embedding calls | 100 chunks per batch | Balances API rate limits against total ingestion time |
| Re-embedding trigger | Any time chunking strategy or embedding model changes | Embeddings from different models are not comparable — mixing them silently corrupts retrieval quality with no visible error |

## 4. Vector store

| Parameter | Value | Rationale |
|---|---|---|
| Local/dev store | Chroma (in-process, file-backed) | Zero setup, good enough for a document set under ~50k chunks, matches the "$0 for local dev" principle |
| Index type | Flat (exact search) for local dev; HNSW if you outgrow flat search performance | Exact search is simpler to reason about and fast enough below ~100k vectors; don't add approximate-search complexity before you need it |
| Similarity metric | Cosine similarity | Standard for normalized text embeddings; matches what most embedding models are trained/evaluated against |

## 5. Retrieval

| Parameter | Value | Rationale |
|---|---|---|
| **top_k** | **5** for simple lookups, **8** for multi-hop research nodes | 5 is the standard starting point — enough coverage without diluting the prompt with marginal matches. Multi-hop gets more because it's actively gathering evidence across sub-questions. |
| Similarity threshold | 0.75 (cosine) — chunks below this are discarded even if they're in the top-k | Prevents the model from being handed a "best available" chunk that isn't actually relevant, just closest by default |
| Reranking | Not required in v1; add a cross-encoder reranker (e.g. `bge-reranker-base`) only if evaluation in Stage 2 shows precision issues | Don't add a second model/latency cost until you have evaluation data proving you need it |
| Metadata filtering | Support filtering by `doc_type` and date range at query time | Lets the router narrow the search space for domain-specific questions (e.g. "runbooks only") without a full reranking pass |

## 6. LLM configuration

| Parameter | Value | Rationale |
|---|---|---|
| Model (generation) | A mid-tier model for development (cost-conscious iteration), swappable via config to a stronger model for the "production" MLflow-registered config in Stage 2 | Iterating Stage 1 logic with an expensive model burns budget on debugging, not on the thing that actually needs a strong model |
| Temperature | 0.1 | RAG answers should be close to deterministic and grounded in retrieved text — high temperature invites the model to embellish beyond the sources |
| Max output tokens | 800 | Long enough for a full cited answer, short enough to keep latency and cost predictable |
| System prompt requirement | Must explicitly instruct: answer only from retrieved context, cite the source for every claim, say "I don't know" rather than fill gaps | This is the single highest-leverage sentence in the whole system for preventing hallucination — don't skip it |

## 7. LangGraph routing

| Parameter | Value | Rationale |
|---|---|---|
| Routing decision method | LLM classification call (cheap/fast model) returning one of `simple_lookup`, `multi_hop`, `clarify` | A lightweight classification pass is far cheaper than always running the expensive multi-hop path "just in case" |
| Clarify trigger | Query classified as ambiguous, or query returns zero chunks above the similarity threshold | Two distinct triggers: genuinely vague questions ("how do I deploy?"), and questions the corpus simply can't answer — both should ask rather than guess |
| Multi-hop trigger | Query implies comparison, causality ("why did X happen and did it affect Y"), or references more than one identifiable topic | Matches the Query 2 example from earlier — spanning two documents is the signal, not just query length |
| Max multi-hop iterations | 3 sub-retrievals before forcing synthesis | Prevents an open-ended research loop from running away in cost/latency; 3 hops covers the large majority of realistic internal-doc questions |
| Conversation memory window | Last 6 turns (3 user + 3 assistant), summarized beyond that | Keeps context relevant without unbounded prompt growth in long sessions |

## 8. Citations

| Parameter | Value | Rationale |
|---|---|---|
| Citation format | Inline reference to `source_path`, optionally with a section/heading if available | Matches what's shown in the earlier usage example — a citation a user can actually go check |
| Minimum citation coverage | Every factual claim in the answer must map to at least one retrieved chunk | This is the enforceable definition of "grounded" — not a suggestion, a hard requirement checked in evaluation |
| Uncited claim handling | If the model can't ground a claim, it must omit the claim or say it doesn't know — never present it uncited | The failure mode to design against is confident, uncited, wrong |

## 9. Evaluation (feeds into Stage 2, define now)

| Parameter | Value | Rationale |
|---|---|---|
| Faithfulness scoring method | LLM-as-judge: does every claim in the answer trace to the retrieved context? (or `ragas` faithfulness metric) | Automatable, doesn't require hand-labeling every response |
| Minimum acceptable faithfulness score | 0.9 (90% of claims grounded) on your test question set | Below this, the config isn't ready to register as "production" in MLflow |
| Test question set size | At least 20 hand-written questions covering simple, multi-hop, and out-of-scope (should-clarify) cases | Small enough to write by hand, large enough to catch regressions when you tune chunking/retrieval later |

## 10. Non-functional requirements

| Parameter | Value | Rationale |
|---|---|---|
| Latency budget | Under 1.5s for simple lookup, under 4s for multi-hop (excluding network/streaming overhead) | Sets a concrete target rather than "make it fast" — both are checkable against Stage 2's logged latency |
| Cost budget | Under $0.01 per simple query, under $0.05 per multi-hop query, at development-model pricing | Keeps iteration affordable; recheck this if you swap to a stronger model for "production" |
| Config location | All of the above live in `agent/src/config.py`, validated via `pydantic-settings`, overridable by environment variable | Nothing above should ever be a hardcoded literal buried in the retrieval or graph code — that's what makes Stage 2's config sweeps possible without editing code |

---

## Summary — the numbers to start with

```python
# agent/src/config.py (defaults — override via env vars per environment)
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "text-embedding-3-small"
TOP_K_SIMPLE = 5
TOP_K_MULTI_HOP = 8
SIMILARITY_THRESHOLD = 0.75
TEMPERATURE = 0.1
MAX_OUTPUT_TOKENS = 800
MAX_MULTI_HOP_ITERATIONS = 3
CONVERSATION_MEMORY_TURNS = 6
FAITHFULNESS_THRESHOLD = 0.9
```

Treat these as the starting hypothesis, not gospel — Stage 2's MLflow sweeps exist specifically to test whether, say, `chunk_size=256` or `top_k=7` actually performs better on *your* document set. The value of specifying exact numbers now isn't that they're correct forever; it's that "correct" becomes something you can measure instead of something you argue about.
