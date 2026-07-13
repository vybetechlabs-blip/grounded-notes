---
title: "SOP: Automation Incident Response"
doc_type: sop
tags: [incidents, oncall, care-plan]
---

# SOP: Automation Incident Response

Owner: Priya Raman. Applies to every system under an Automation Care Plan.
Care Plan clients get a dedicated incident email address that pages the on-call
rotation.

## Severity levels

- **Minor** — automation degraded but work can continue manually; no data
  loss. Response: next business day.
- **Major** — automation stopped or producing wrong output that reaches
  customers or books. Response: 4 business hours. Only Priya (or Maya in her
  absence) can declare a major incident, and the client is informed the moment
  it is declared.

## Response steps

1. **Acknowledge** to the client within the response window, even if the cause
   is unknown. "We see it, we're on it, next update at HH:MM."
2. **Stabilize before diagnosing.** Pause the automation or fail over to the
   documented manual process from the runbook. A paused pipeline is an
   inconvenience; a wrong-output pipeline is a cleanup project.
3. **Check the dead-letter queue first.** Every Lanternfish automation ships
   with a dead-letter queue and alerting (see Tooling Stack). Most incidents
   are visible there before anywhere else.
4. **Fix, replay, verify.** Replay dead-lettered items after the fix, then
   verify counts end-to-end against the source system.
5. **Write the incident note** within 24 hours: timeline, root cause, items
   replayed, and what will prevent recurrence. Sent to the client unedited —
   the same note we read internally.

## Rules

- Never diagnose live on a client call. Acknowledge, drop, investigate, report.
- No fix ships without being reproduced in the staging copy first, however
  urgent it feels. The Granite Peak retro documents the one time we broke this
  rule and what it cost.
- Two major incidents on the same root cause within a quarter triggers a free
  architecture review — our defect, our dime.
