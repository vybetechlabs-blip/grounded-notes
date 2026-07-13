---
title: "Retro: Tidewater Marine Supply — Catalog Assistant"
doc_type: retro
tags: [retro, assistant, retrieval, evals, lessons]
---

# Retro: Tidewater Marine Supply — Catalog Assistant (November 2025)

**Engagement:** Grounded Assistant Build — assistant answering product-spec
and compatibility questions over a 12,000-item marine parts catalog plus
installation guides.
**Team:** Sam (delivery lead), Priya.
**Outcome:** Shipped on time, best eval numbers of any engagement to date.
Client took the Care Plan and commissioned a follow-on chatbot scoping.

## What happened

The catalog corpus was the hardest retrieval problem we had faced: part
numbers, superseded SKUs, and abbreviation-dense installation guides. The
first vector-only build sat at 71% retrieval hit-rate on the 60-question eval
set — users asking for "TW-4417 gasket torque spec" got semantically-similar
but wrong parts. Sam added a BM25 lexical index and fused it with the vector
scores via reciprocal-rank fusion; hit-rate jumped to 89% with no other
changes. That experience is now the "why hybrid" section of the RAG
Implementation Playbook.

Late in the project, a prompt tweak intended to make answers friendlier
doubled unsupported claims on the eval set — caught before deploy because
prompt changes run the eval gate like code changes (see Prompt Engineering
Standards).

## What went well

- Eval-first development. Building the 60-question set in week one (sourced
  from the client's counter staff, not from us) made every retrieval decision
  measurable instead of arguable.
- Superseded-SKU handling: an ingestion rule tags superseded parts and the
  prompt template makes the assistant say "TW-4417 was replaced by TW-4417B"
  instead of answering for the dead part.

## What went badly

- We underestimated ingestion time for the installation-guide PDFs; layout
  extraction ate four unplanned days. PDFs get their own line item in every
  future estimate.

## Changes adopted (now house rules)

1. Hybrid retrieval is the default for every assistant build (RAG playbook).
2. Eval questions are sourced from client staff, never written by the build
   team alone.
3. PDF-heavy corpora get an explicit ingestion-complexity line in the proposal.
