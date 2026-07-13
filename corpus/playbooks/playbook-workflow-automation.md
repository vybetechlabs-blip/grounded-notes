---
title: "Playbook: Workflow Automation"
doc_type: playbook
tags: [automation, integration, delivery]
---

# Playbook: Workflow Automation

Owner: Priya Raman. The delivery pattern for Automation Sprints.

## Picking the right workflow

The best first automation scores high on all three:

1. **Frequency** — runs daily or more.
2. **Rule-clarity** — a human can write the rules down; exceptions are
   enumerable.
3. **Pain** — someone dreads it or errors are costly.

The discovery call should surface 3–5 candidates; the sprint automates exactly
one. Resist bundling ("while you're in there…") — that instinct is why the
sprint is fixed-scope.

## Build standards

- **Idempotency first.** Every step must be safe to run twice. Retries and
  replays are not edge cases; they are Tuesday.
- **Dead-letter queue always.** Items that fail processing land somewhere
  visible with the error attached, and something alerts a human (see Tooling
  Stack). Silent drops are how automations lose trust.
- **Manual fallback documented.** The runbook includes the manual process for
  when the automation is paused (see Automation Incident Response SOP).
- **Checkpoint long jobs.** Anything processing hundreds of items writes
  progress so a crash resumes instead of restarting.

## The mid-sprint demo

Week two of every sprint demos against **real data** in a staging copy. Demos
on toy data hide the exact problems that kill automations: dirty inputs,
weird encodings, the one record from 2019 with a null where no null should be.
The Cobble & Crane retro is the canonical example of why this demo is not
optional.

## Handoff

Follows the Project Handoff SOP, with one automation-specific addition: the
client's operator pauses and resumes the automation themselves during the
handoff session. If they can't, the runbook failed the empty-chair test.
