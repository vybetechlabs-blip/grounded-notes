---
title: Tooling Stack
doc_type: company
tags: [tools, stack, internal]
---

# Tooling Stack

What we use internally and what we deploy for clients. Priya owns this doc;
propose changes in the #tooling channel before editing.

## Internal operations

- **Project tracking:** Linear-style kanban, one board per engagement, columns
  fixed by the Project Kickoff SOP (Backlog / In Progress / Client Review / Done).
- **Documents:** Markdown in a shared repo. Proposals and reports are generated
  from templates — never written from scratch.
- **Time tracking:** none. We sell fixed scope, not hours.

## Client-facing delivery

- **Automations:** hosted workflow runners with version-controlled definitions.
  Every automation must have a dead-letter queue and an alert route before it
  ships — no silent failures (see Automation Incident Response SOP).
- **Assistants:** retrieval-augmented generation over the client's documents.
  Default architecture per the RAG Implementation Playbook: local or hosted
  embeddings, a vector store the client controls, hybrid retrieval, and a
  grounding check that refuses out-of-corpus questions.
- **Chatbots:** same retrieval core as assistants, plus the escalation-to-human
  flow from the Support Chatbot Playbook.

## Model policy

We are provider-agnostic and quote model costs as a pass-through. Defaults:

- Embeddings: small local models on CPU unless the corpus exceeds ~50k chunks.
- Generation: the client's preferred cloud provider; if the client has no
  preference, we recommend based on the LLM Vendor Selection Playbook.
- We never fine-tune as a first resort. Retrieval fixes most "the model doesn't
  know our business" complaints at a fraction of the cost.

## Security defaults

- Client credentials live in the client's own secret manager, never in ours.
- All demo data is synthetic until the client signs the data processing
  addendum (see Data Handling and Privacy SOP).
