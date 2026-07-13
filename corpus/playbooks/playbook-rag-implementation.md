---
title: "Playbook: RAG Implementation"
doc_type: playbook
tags: [rag, retrieval, assistants, architecture]
---

# Playbook: RAG Implementation

Owner: Sam Alvarez. The delivery pattern behind every Grounded Assistant
Build. Read this before scoping one.

## The architecture in one paragraph

Ingest the client's documents into chunks that preserve heading context; embed
chunks with a small model (local CPU models are fine below ~50k chunks); store
in a vector database the client controls; retrieve with **hybrid search** —
lexical (BM25) and vector scores fused — because names, SKUs, and acronyms are
exactly what pure vector search fumbles; assemble retrieved chunks with source
attribution; generate an answer that must cite its sources; and **refuse** when
retrieval confidence is below threshold.

## Why hybrid retrieval

Client corpora are full of exact tokens that matter: product codes, people's
names, error strings. Vector similarity smears these; BM25 nails them but
misses paraphrase. Fusing both (reciprocal-rank fusion is simple and robust)
raised answer hit-rate on the Tidewater project from 71% to 89% with no other
changes. Default to hybrid; drop to vector-only only if the corpus is tiny.

## Why the grounding hard-fail

An assistant that answers everything is worse than no assistant: users cannot
tell confident-right from confident-wrong. We set a retrieval-confidence
threshold during evaluation; below it the assistant answers "I don't have that
in the knowledge base" and shows what it *did* find. Clients push back on this
during scoping ("can't it just try?") — hold the line. The refusal is the
feature that makes the rest trustworthy.

## Evaluation gate

No assistant ships without an eval set: 20+ real questions with
expected-source labels, run on every significant change. Track two numbers —
retrieval hit-rate (expected doc in top-k) and grounding accuracy
(out-of-scope questions correctly refused). Ship threshold: 85% hit-rate,
100% of the refusal set refused.

## Common failure modes

- **Chunks without context:** a chunk that says "increase it to 40" is useless
  without its heading trail. Prepend heading context to every chunk.
- **Stale index:** re-ingestion must be idempotent and scheduled; a knowledge
  base that silently drifts from the source documents erodes trust in a month.
- **Eval theater:** an eval set written by the same person who wrote the
  chunker will test what the chunker is good at. Source questions from the
  client's actual staff.
