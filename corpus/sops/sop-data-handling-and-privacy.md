---
title: "SOP: Data Handling and Privacy"
doc_type: sop
tags: [security, privacy, credentials]
---

# SOP: Data Handling and Privacy

Owner: Maya Okonkwo. These rules are contractual commitments, not aspirations.
Violations are reportable to the client under our standard terms.

## Credentials

- Client credentials live in the **client's** secret manager. Lanternfish
  never stores client credentials in our own vaults, repos, or laptops.
- Access is requested read-only first; write access only when the build
  requires it, and it is listed in the access log.
- At offboarding, all our accounts are revoked within 5 business days and the
  client confirms the system runs without them (see Project Handoff SOP).

## Client data

- Real client data does not leave the client's systems. Development happens
  against synthetic or masked data until the data processing addendum is
  signed.
- No client data in prompts sent to shared model endpoints unless the client
  has approved the provider in writing. The LLM Vendor Selection Playbook
  records each provider's data-retention stance to support that conversation.
- Laptops: full-disk encryption mandatory; client data never in personal
  cloud-sync folders.

## Retention

- Engagement folders are archived at offboarding and purged of any client data
  extracts within 90 days. What we keep: our code, our docs, the retro.
- Incident notes are kept indefinitely (they contain timelines, not data).

## AI-specific rules

- Assistants we build must carry the grounding hard-fail behavior: if the
  answer is not in the client's documents, the assistant says so. An assistant
  that guesses is a liability engine (see RAG Implementation Playbook).
- Evaluation sets for client assistants are built from the client's real
  questions but scrubbed of personal data before entering the eval repo.

## If something leaks

Tell Maya first, the client within 24 hours, in writing, with what/when/scope.
There is no severity threshold below which we stay quiet.
