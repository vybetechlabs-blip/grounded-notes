---
title: "Retro: Granite Peak Property Management — Maintenance Assistant"
doc_type: retro
tags: [retro, assistant, data-readiness, incident, lessons]
---

# Retro: Granite Peak Property Management — Maintenance Assistant (September 2025)

**Engagement:** Grounded Assistant Build — internal assistant answering
maintenance-policy questions for property managers across 30 buildings.
**Team:** Maya (delivery lead), Sam, Jonah.
**Outcome:** Delivered late with reduced scope. The most instructive failure
in the company's history; two standing rules trace here.

## What happened

Granite Peak declined the Data Readiness Assessment ("our docs are fine, we
just migrated wikis"). Theo took the build anyway — pipeline was thin that
month. The document set turned out to be three generations of policy wikis,
mutually contradictory, with no owner able to say which version governed. Sam's
retrieval worked; the corpus itself disagreed with itself, so grounded answers
were *correctly citing wrong documents*.

Mid-project, under schedule pressure, we hot-patched the ingestion filter
directly in the staging-shared environment to exclude a deprecated wiki — the
patch had a path glob error, silently excluded 40% of the valid corpus, and
for two days the assistant refused questions it had answered the week before.
The client noticed before we did.

## What went well

- The grounding hard-fail behaved exactly as designed: with the corpus
  hollowed out, the assistant refused rather than inventing policy. A guessing
  assistant would have been quoting phantom rules to 30 buildings.
- The recovery: we froze scope to the 60% of policy areas with a confirmed
  governing document, hit the eval gate on that subset, and shipped honestly.

## What went badly

- Skipping the readiness assessment was the root cause; everything else was
  downstream.
- The un-reproduced hot-patch. Two days of degraded service from a change that
  a staging replay would have caught in minutes.

## Changes adopted (now house rules)

1. **Below-40 readiness scores are declined in writing** — and the readiness
   assessment is a hard prerequisite for every Grounded Assistant Build
   (see Service Catalog and Engagement Models and Pricing).
2. **No fix ships without staging reproduction**, however urgent — written
   into the Automation Incident Response SOP, citing this retro.
