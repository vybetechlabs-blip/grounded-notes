# grounded-notes

A grounded RAG knowledge assistant: ask questions over a document corpus and get
**cited answers** — or an honest *"that's not in the corpus"* when the documents
don't contain the answer.

> Status: under construction. This README is filled in phase by phase as the
> build progresses.

## What it does

- Ingests a folder of markdown/text docs (a synthetic consultancy knowledge base ships in `corpus/`)
- Chunks with heading-aware overlap, embeds locally on CPU (no API key needed)
- Hybrid retrieval (BM25 + vectors), answers with source citations
- **Grounding hard-fail:** unanswerable questions are refused, not hallucinated
- Optional cloud LLM upgrade (Claude / OpenAI) behind an env var

## Quickstart

```bash
git clone <this repo>
cd grounded-notes
uv sync
uv run ragkit ingest
uv run ragkit query "How does Lanternfish structure a project kickoff?"
```

No API key required — the default path uses local sentence-transformers
embeddings and an extractive answerer.

## Architecture

*(filled in during Phase 1–2)*

## Eval results

Committed cases in [`evals/cases.yaml`](evals/cases.yaml), run with `uv run ragkit eval`:

| Metric                              | Result | Cases |
| ----------------------------------- | ------ | ----- |
| Retrieval hit-rate@5                | 100%   | 15 answerable questions |
| Refusal accuracy (grounding guard)  | 100%   | 4 out-of-corpus questions |
| Grounding accuracy overall          | 100%   | 19 |

These numbers weren't free: the first eval run scored 93% / 50%. The two
failure classes it exposed (same-entity questions with no answer in the
corpus; rare-term chunks drowned in rank fusion) drove the two-signal
grounding guard and the term-coverage guarantee in fusion. Details in
Design decisions.

## Live demo

*(filled in during Phase 4)*

## Design decisions

*(filled in during Phase 4)*
