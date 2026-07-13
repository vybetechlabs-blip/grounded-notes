---
title: "Retro: Bluebird Dental Group — Intake Automation"
doc_type: retro
tags: [retro, automation-sprint, lessons]
---

# Retro: Bluebird Dental Group — Intake Automation (March 2025)

**Engagement:** Automation Sprint — automate new-patient intake from web form
to practice-management system across four clinic locations.
**Team:** Priya (delivery lead), Jonah.
**Outcome:** Shipped one week late; client satisfied after a rocky middle.
Took the Care Plan.

## What happened

Discovery scoped the intake flow from the head office's description. Week one
built against that description. The week-two demo — run on toy data because
the staging copy wasn't ready — looked great. Then we got real form
submissions: two of the four locations had customized their web forms years
ago, with different field names and a consent checkbox the head office didn't
know existed. Week three became a rebuild of the field-mapping layer, and we
slipped a week.

## What went well

- The dead-letter queue design meant mis-mapped records piled up visibly
  instead of vanishing; nothing was lost, and the client saw exactly what was
  quarantined and why.
- Priya's daily written updates during the slip kept the client calm — they
  knew the size of the problem before they could worry about it.

## What went badly

- We demoed on toy data. The customized forms would have surfaced in
  five minutes with real submissions.
- Discovery talked to the head office only. Nobody who actually operated the
  location forms was in the room.

## Changes adopted (now house rules)

1. **Mid-point demos run on real client data, always.** This is now in the
   Project Kickoff SOP as a hard rule.
2. Discovery calls for multi-location clients include at least one person who
   operates the process daily, per location variant.
3. The field-mapping layer Priya built became a reusable library component.
