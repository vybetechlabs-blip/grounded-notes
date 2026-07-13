---
title: "Playbook: Support Chatbot Deployment"
doc_type: playbook
tags: [chatbot, support, escalation]
---

# Playbook: Support Chatbot Deployment

Owner: Sam Alvarez. For customer-facing deflection bots scoped to a client's
help-center content. Shares the retrieval core with the RAG Implementation
Playbook; this doc covers what is different when the user is a customer, not
an employee.

## Scope rules

- One channel first (web widget *or* email), one language, one product line.
  Expansion is a follow-on engagement, not scope creep.
- The bot answers only from the approved content set: help-center articles,
  the client FAQ, and policy pages the client explicitly whitelists.
- Anything involving refunds, account changes, or legal topics routes to a
  human regardless of retrieval confidence. This list is agreed in writing at
  kickoff.

## The escalation-to-human flow (non-negotiable)

Every conversation offers a visible path to a person. The bot escalates
automatically when: retrieval confidence is below threshold (the grounding
hard-fail), the customer expresses frustration, the same question repeats
twice, or the topic is on the always-human list. Escalation hands over the
full transcript so the customer never repeats themselves — that handover is
the single biggest satisfaction driver we have measured.

## Tone and honesty

- The bot introduces itself as a bot. No human names, no fake typing delays.
- Refusals are helpful: "I don't have that in the help center — here's a
  human" beats an apology loop.

## Launch gates

1. Eval set of 30+ real customer questions passes the same thresholds as the
   RAG playbook (85% hit-rate, 100% refusal accuracy).
2. Two-week shadow mode: the bot drafts answers agents review before anything
   reaches a customer. Petal & Stem's shadow mode caught a pricing-page
   staleness problem that would have been very public.
3. A weekly quality dashboard the client can read: deflection rate, escalation
   rate, and a sampled answer-quality score.

## Metrics that matter

Deflection rate is the headline, but escalation *quality* keeps the contract:
a bot that deflects 40% and hands off the rest gracefully outperforms a bot
that deflects 60% and traps the other 40% in loops.
