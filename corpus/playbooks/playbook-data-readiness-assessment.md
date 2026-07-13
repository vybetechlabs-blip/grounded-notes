---
title: "Playbook: Data Readiness Assessment"
doc_type: playbook
tags: [data, assessment, diagnostic]
---

# Playbook: Data Readiness Assessment

Owner: Jonah Petit (delivery), Maya Okonkwo (review). A one-week diagnostic
that answers: *can this client's data support what they want to build?* Sold
standalone or as week one of a Grounded Assistant Build.

## The four scoring dimensions (25 points each)

1. **Access** — can we actually get to the data? APIs, exports, permissions,
   and who can grant them. A perfect dataset behind a six-week IT ticket
   queue scores low.
2. **Quality** — completeness, freshness, and consistency, sampled rather
   than assumed. We pull real samples and count: null rates, duplicate rates,
   date ranges, format drift.
3. **Coverage** — does the data contain the answers the client wants the
   system to give? For assistant projects this means mapping 20 real questions
   from client staff against the document set and counting how many are
   answerable at all.
4. **Governance** — is there an owner, a retention rule, and clarity on what
   may be sent to which vendors (see Data Handling and Privacy SOP)?

## Scoring bands

- **80–100:** build-ready. Proceed to proposal.
- **60–79:** build with remediation items in scope (they go in the contract).
- **40–59:** remediation engagement first; a build now would disappoint.
- **Below 40:** we decline the build and say why in writing. This band is
  contractual — see "What we refuse" in Engagement Models and Pricing.

## The week

Days 1–2 inventory and access checks; day 3 sampling and quality counts; day 4
the coverage mapping exercise with client staff; day 5 scoring, the written
recommendation, and a 45-minute readout call.

## Rules

- Scores come with evidence: every dimension's score cites the samples or
  tickets behind it. An assessment without receipts is an opinion.
- Jonah drafts, Maya reviews, and the readout never softens a below-40 score.
  The Granite Peak engagement went ahead on a "surely it'll be fine" — read
  that retro.
