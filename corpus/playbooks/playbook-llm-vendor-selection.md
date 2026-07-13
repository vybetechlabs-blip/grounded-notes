---
title: "Playbook: LLM Vendor Selection"
doc_type: playbook
tags: [llm, vendors, models, procurement]
---

# Playbook: LLM Vendor Selection

Owner: Sam Alvarez. How we recommend a model provider when a client has no
existing preference. We are provider-agnostic; model fees pass through at cost
(see Tooling Stack).

## The selection criteria, in order

1. **Data-retention stance.** Does the provider train on API traffic? What are
   the retention windows and the zero-retention options? This is a gating
   criterion, not a preference — a provider without an acceptable answer is
   out regardless of quality (see Data Handling and Privacy SOP).
2. **Task fit at the small end.** Most client workloads are retrieval-grounded
   answering, extraction, and summarization. Benchmark the provider's *small*
   models on the client's eval set first; the small model plus good retrieval
   usually beats a big model with lazy retrieval, at a tenth the cost.
3. **Latency and rate limits** at the client's realistic peak, not the demo.
4. **Operational maturity.** Status page history, deprecation policy, SDK
   quality. Model deprecations are a real maintenance cost for Care Plan
   systems.
5. **Price last.** Token prices change quarterly; architecture outlives them.

## Process

Run the client's eval set (from the RAG playbook gate) against 2–3 candidate
providers' small and mid models. Present a one-page comparison: quality on
their questions, monthly cost projection at their volume, retention terms.
The client picks; we record the choice and the runner-up in the decision log
so a future switch is cheap.

## Standing guidance

- Design for provider swap: all model calls go through one interface in our
  standard architecture. Switching providers should be a config change plus an
  eval run, not a rewrite.
- Embeddings and generation are separate decisions. Local embedding models on
  CPU cover most corpora free of charge; paying embedding fees for a 2,000-doc
  knowledge base is waste.
- Re-run the comparison at each Care Plan annual review; the market moves.
