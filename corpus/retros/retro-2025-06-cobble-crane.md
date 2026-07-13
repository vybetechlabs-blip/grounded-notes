---
title: "Retro: Cobble & Crane Logistics — Invoice Reconciliation"
doc_type: retro
tags: [retro, automation-sprint, reporting, lessons]
---

# Retro: Cobble & Crane Logistics — Invoice Reconciliation (June 2025)

**Engagement:** Automation Sprint — automate matching carrier invoices against
shipment records and flag discrepancies.
**Team:** Priya (delivery lead), Sam.
**Outcome:** Shipped on time; relationship nearly damaged by a reporting
failure on our side. Client renewed anyway.

## What happened

The build went fine technically. The problem was ours: in week two, Priya
found that the client's shipment export was missing roughly 8% of records —
a client-side data problem that put the discrepancy-flagging accuracy at risk.
The weekly status went out GREEN with a soft note "investigating some export
gaps." It should have been YELLOW with a named decision: *someone on your side
needs to fix the export job, this week, or the accuracy target moves.*

The client's ops manager first understood the severity in week three, felt
blindsided, and said so on the status call. Fair. We recovered by re-scoping
the accuracy target against the fixable portion and delivering exactly that,
but the trust repair cost more energy than the whole build.

## What went well

- The reconciliation engine itself: idempotent, replayable, dead-letter queue
  from day one — textbook Workflow Automation Playbook.
- Once the export was fixed (week four, client-side), replaying the backlog
  took twenty minutes and matched hand-counts exactly.

## What went badly

- We softened a YELLOW to GREEN to keep the mood pleasant. Never again.

## Changes adopted (now house rules)

1. Status definitions are now written into the Weekly Status Reporting SOP,
   and every YELLOW must name the decision and the decider. "Softening a
   YELLOW" is called out there by name, citing this retro.
2. Client-side data problems get their own line in the written status from
   the week they are found — they are scope risks, not footnotes.
