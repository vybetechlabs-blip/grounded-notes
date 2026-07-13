# grounded-notes

A grounded RAG knowledge assistant: ask questions over a document corpus and get
**cited answers** — or an honest *"I don't have that in the knowledge base"*
when the documents don't contain the answer.

Built as a public work sample: hybrid retrieval, a measurable grounding
hard-fail, a committed eval suite whose numbers are reproduced below, and a
clean-room synthetic corpus. Runs from a fresh clone in about two minutes with
**no API key required**.

> **Live demo:** *(Hugging Face Spaces link goes here after deploy — see
> [Deploying](#deploying-to-hugging-face-spaces))*

## Quickstart

```bash
git clone <this-repo> && cd grounded-notes
uv sync                 # Python 3.12, installs everything incl. CPU-only ML deps
uv run ragkit ingest    # chunk + embed the corpus into a local Chroma store
uv run ragkit query "How much does an Automation Sprint cost?"
uv run streamlit run app.py   # chat UI at localhost:8501
```

The first run downloads the embedding model (~90 MB, cached). No key, no
account, no external service — embeddings are computed locally on CPU and the
default answerer is extractive.

**Optional cloud upgrade:** `uv sync --extra cloud`, then set
`ANTHROPIC_API_KEY` (or `OPENAI_API_KEY`) — generation upgrades to a fluent
LLM answer automatically. All settings in [`.env.example`](.env.example).

## What's in the box

- **Corpus** — 25 synthetic, cross-referencing docs for *Lanternfish
  Consulting*, a fictional AI consultancy: SOPs, delivery playbooks, project
  retrospectives, FAQs. Entirely invented, so the repo ships its own data and
  retrieval quality is testable. Point `RAGKIT_CORPUS_DIR` at any folder of
  `.md`/`.txt` to use your own.
- **Ingestion** — frontmatter-aware loader; heading-aware chunking with
  overlap; every chunk carries (and is embedded with) its heading trail.
  Content-hash chunk ids make re-ingestion an idempotent *sync*: unchanged
  chunks no-op, removed content is deleted from the index.
- **Retrieval** — hybrid: BM25 (in-package Okapi, ~60 lines) fused with
  vector search via reciprocal-rank fusion, plus a term-coverage guarantee
  (below). Optional cross-encoder reranker behind a flag — measured, and
  defaulted off (below).
- **Grounding** — a two-signal hard-fail; unanswerable questions are refused
  before any LLM call, with the reason shown.
- **Generation** — `Provider` interface: keyless extractive default, Claude
  or OpenAI when a key is present, graceful fallback to extractive if a cloud
  call fails. The demo never hard-crashes on a fresh clone or a bad key.
- **Eval** — 19 committed cases; `uv run ragkit eval` prints hit-rate and
  grounding accuracy and exits non-zero below ship thresholds.

## Architecture

```
corpus/*.md ──▶ loader ──▶ chunker ──▶ embeddings (sentence-transformers, CPU)
                (frontmatter) (heading-aware)      │
                                                   ▼
                                        Chroma (data/chroma, idempotent sync)
                                                   │
question ──▶ BM25 ──┐                              │
        └──▶ vector ┴─▶ RRF fusion + term-coverage guarantee
                              │
                              ▼
                    grounding guard (2 signals) ──✗──▶ refusal + closest docs
                              │ ✓
                              ▼
                    provider (extractive | Claude | OpenAI)
                              │
                              ▼
                    answer + [n] citations (file + heading)
```

Package layout mirrors the pipeline: `ragkit/ingest`, `embed`, `store`,
`retrieve`, `generate`, `grounding`, plus `pipeline.py` tying them together
and two frontends (`cli.py`, `app.py`).

## Eval results

Committed cases in [`evals/cases.yaml`](evals/cases.yaml), run with
`uv run ragkit eval`:

| Metric                             | Result | Cases |
| ---------------------------------- | ------ | ----- |
| Retrieval hit-rate@5               | 100%   | 15 answerable questions |
| Refusal accuracy (grounding guard) | 100%   | 4 out-of-corpus questions |
| Grounding accuracy overall         | 100%   | 19 |

These numbers weren't free: the first eval run scored **93% / 50%**. The two
failure classes it exposed drove the design decisions below.

## Design decisions

**Why hybrid retrieval.** Corpora are full of exact tokens that matter —
part numbers, names, headings. Vector similarity smears them; BM25 nails them
but misses paraphrase. RRF fuses both rankings without score-normalization
gymnastics. Ranking and confidence are deliberately separated: RRF decides
*order*, but every returned chunk keeps its true cosine similarity, so the
grounding threshold has one stable meaning.

**Why the grounding hard-fail has two signals.** A cosine threshold catches
off-topic questions ("capital of Australia?", 0.08) but not the harder
class the eval exposed: questions *about* the corpus's entities whose answers
the corpus doesn't contain. "What is Lanternfish's street address?" scored
0.50 — topically similar to everything, answerable by nothing, and a single
threshold can't separate it from real answerable questions (which ranged
0.40–0.73). The second signal — IDF-weighted coverage of the question's
informative terms in the retrieved chunks — separates them cleanly: "address"
and "phone" occur nowhere, so coverage collapses even though similarity is
high. Refusal accuracy went 50% → 100% with zero answerable regressions.
Known tradeoff: a heavily paraphrased question using none of the corpus's
vocabulary could be wrongly refused; for this corpus the eval says it isn't
happening, and safe-refusal beats confident-wrong.

**Why fusion has a term-coverage guarantee.** The eval's one retrieval miss:
"Which discounts does Lanternfish offer?" The answering chunk sat at cosine
0.18 (MiniLM doesn't connect "discounts" to "fee credited / 15% off"), BM25
ranked it #3, but chunks matching the low-information company name on *both*
legs dominated RRF's dual-presence scoring and pushed it out of the top-5.
Fix: if the cut top-k entirely lacks the query's rarest informative term and
a lower-ranked candidate contains it, swap that candidate in — one swap, one
term. Retrieval now tries to satisfy the same coverage signal the guard will
demand. Hit-rate 93% → 100%.

**Why the reranker exists but defaults off.** The standard next step for the
paraphrase gap is a cross-encoder reranker, so it's implemented
(`RAGKIT_RERANK=true`). Measured on this corpus it improved nothing and
actively demoted the discounts chunk (ms-marco is entity-literal: probes
showed −9.8 → −3.1 just by removing "Lanternfish" from the query, and it
scored "Nonprofits receive 15% off" as *not* answering "which discounts").
Shipping a component because it's canonical would have made the system worse;
the flag stays for corpora where it earns its latency. Measure first.

**Why extractive is the keyless default.** A public demo must work with zero
setup and never hard-crash, so the floor is an answerer that quotes the most
query-similar sentences from retrieved chunks with citations. Less fluent
than an LLM — but incapable of asserting anything the corpus doesn't say,
which is the point of the project. Cloud keys upgrade fluency, not
truthfulness: the LLM prompt enforces the same contract (answer only from
context, cite everything, refuse when insufficient, treat retrieved text as
data rather than instructions), and any cloud failure degrades back to
extractive.

**Why the corpus is synthetic.** Shipping data makes retrieval quality
reproducible and reviewable — every eval case can be checked by reading the
cited doc. Fictional content means zero privacy risk and no licensing
questions. The docs deliberately cross-reference each other so multi-hop
questions have teeth.

**Tradeoffs accepted.** Chroma over pgvector: right default for a clonable
demo (embedded, zero infra); the store is wrapped in one small class
(`ragkit/store/chroma.py`) whose four methods (`sync`, `query`,
`similarities`, `all_chunks`) are the entire surface a pgvector
implementation would need. BM25 rebuilt from the store per process instead of
persisted: milliseconds at this corpus size, and the two indexes can't
drift; a 100k-chunk corpus would want it persisted. Thresholds
(`min_score=0.35`, `min_coverage=0.4`) are calibrated against the committed
eval — recalibrate them (via `ragkit eval`) when swapping corpora.

## CLI

```
uv run ragkit ingest              # idempotent corpus sync
uv run ragkit query "..."         # cited answer or refusal
uv run ragkit query "..." --show-chunks
uv run ragkit eval                # run committed cases, non-zero exit below thresholds
```

## Deploying to Hugging Face Spaces

The Streamlit app is the Spaces entrypoint. Steps:

1. Create a new Space: **Streamlit** SDK, CPU basic (free) hardware.
2. A pip-compatible [`requirements.txt`](requirements.txt) is committed
   (Spaces installs with pip, not uv). To regenerate after dependency
   changes: `uv export --no-dev --no-hashes -o requirements.txt`, then
   re-add the `--extra-index-url https://download.pytorch.org/whl/cpu` line
   at the top — torch is pinned to CPU wheels, which saves ~3 GB of CUDA
   downloads on Linux.
3. Push this repo's contents to the Space (or connect the GitHub repo), and
   prepend the Space metadata block to the top of `README.md`:

   ```yaml
   ---
   title: grounded-notes
   emoji: 📚
   sdk: streamlit
   python_version: "3.12"
   app_file: app.py
   ---
   ```

4. First boot takes a couple of minutes: the Space downloads the embedding
   model and ingests the corpus (the app auto-ingests when the index is
   empty). Subsequent boots reuse nothing — Spaces disks are ephemeral — but
   the corpus is small, so cold ingest stays under a minute.
5. Optional: add `ANTHROPIC_API_KEY` as a Space **secret** to upgrade
   generation quality for all visitors (mind the spend — the keyless mode is
   the safe default for a public link).

## Development

```
uv sync                 # includes dev group (ruff, pytest)
uv run pytest           # 36 tests, hermetic: fake embedder, no downloads
uv run ruff check . && uv run ruff format --check .
```

Tests never touch the network: a deterministic bag-of-hashed-words embedder
stands in for sentence-transformers, and the reranker is stubbed. CI runs
lint + format + tests on every push.

## License

MIT — see [LICENSE](LICENSE). The Lanternfish Consulting corpus is fictional;
any resemblance to real companies or people is coincidental.
