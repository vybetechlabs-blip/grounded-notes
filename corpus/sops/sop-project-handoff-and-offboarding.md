---
title: "SOP: Project Handoff and Offboarding"
doc_type: sop
tags: [handoff, offboarding, documentation]
---

# SOP: Project Handoff and Offboarding

Owner: Maya Okonkwo. The engagement is not done when the software works; it is
done when the client can run it without us. Handoff is a deliverable with its
own checklist, and Maya personally approves every one.

## Handoff checklist

1. **Runbook delivered.** A step-by-step operations guide a non-engineer can
   follow: how to check health, restart, read alerts, and who to call. Written
   per the documentation templates, reviewed by someone who did not build the
   system.
2. **Credentials transferred.** Every credential lives in the client's secret
   manager. We hold nothing after offboarding (see Data Handling and Privacy
   SOP). This is verified by logging out of everything and having the client
   confirm the system still runs.
3. **Recorded walkthrough.** A 30–45 minute screen recording of the delivery
   lead operating the system: normal operation, one simulated failure, one
   recovery. Clients rewatch these long after they stop reading docs.
4. **Handoff session.** Live 60-minute session with the client's operators.
   They drive; we watch. Any step they stumble on is a documentation bug and
   gets fixed before sign-off.
5. **Final invoice and sign-off.** The remaining 50% invoices at sign-off.
   Sign-off means the sponsor confirms in writing that the checklist is done.

## Offboarding

- Access revocation: all Lanternfish accounts on client systems are removed
  within 5 business days of sign-off. Noor runs the revocation list.
- Engagement folder archived; retro scheduled within 2 weeks while memory is
  fresh (retros are mandatory, not optional — see any doc in `retros/`).
- Care Plan offer: made once, at sign-off, never pushed. Roughly half of
  clients take it.

## The empty-chair test

Before declaring handoff-ready, the delivery lead asks: "If everyone at
Lanternfish disappeared tomorrow, could the client's team keep this alive with
what they have?" If the honest answer is no, handoff is not ready.
