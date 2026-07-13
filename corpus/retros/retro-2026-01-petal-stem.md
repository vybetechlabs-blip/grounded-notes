---
title: "Retro: Petal & Stem Florists — Support Chatbot"
doc_type: retro
tags: [retro, chatbot, support, lessons]
---

# Retro: Petal & Stem Florists — Support Chatbot (January 2026)

**Engagement:** Support Chatbot Deployment — order-status and care-question
deflection for an online florist with strong seasonal peaks.
**Team:** Sam (delivery lead), Noor (client comms).
**Outcome:** Shipped on time, live before Valentine's peak. Deflection 38%,
escalation satisfaction higher than the human-only baseline.

## What happened

A clean run of the Support Chatbot Playbook, with one save and one surprise.

**The save:** during the mandatory two-week shadow mode, agents reviewing the
bot's drafted answers noticed it kept citing last season's delivery-cutoff
dates. The help-center pricing and delivery pages were stale — a client
content problem no one had noticed because human agents were correcting for it
from memory. The client updated the pages before launch; shadow mode caught
what would have been a very public wrong-answer generator during the
Valentine's rush.

**The surprise:** customers *thanked* the bot for its refusals. The playbook's
honest-refusal wording ("I don't have that in the help center — let me get you
a person, they'll see this conversation") tested better in CSAT comments than
any answer the bot gave. Escalation-with-transcript is the feature customers
mentioned by name.

## What went well

- Shadow mode earning its permanent place as a launch gate.
- Seasonal load: Valentine's week traffic was 9x baseline; the always-human
  routing list (refunds, address changes) kept the bot out of the
  conversations where a mistake is unrecoverable.

## What went badly

- We scoped the weekly quality dashboard as a build-week task; it slipped to
  post-launch because the peak came first. Client was gracious; the playbook
  now sequences the dashboard before launch, not after.

## Changes adopted (now house rules)

1. Content freshness check added to the Support Chatbot Playbook launch gates —
   stale source pages are found in shadow mode at the latest, ideally in the
   coverage mapping (see Data Readiness Assessment Playbook).
2. The quality dashboard ships *before* launch. Non-negotiable ordering.
