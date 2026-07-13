---
title: Internal FAQ
doc_type: faq
tags: [faq, internal, operations]
---

# Internal FAQ

Quick answers for the team. When in doubt, the SOP is authoritative; this page
just saves you the lookup.

## A prospect wants something outside the five catalog services. Who decides?

Custom work needs principal sign-off — bring it to Theo with a one-paragraph
scope sketch. Default answer is no; the catalog exists because custom scoping
is where margins and timelines go to die.

## Can I start building before access is fully confirmed?

No. Kickoff itself is blocked on confirmed access (Client Onboarding SOP,
step 7). If you're tempted, reread the Bluebird Dental retro — week-one
momentum on wrong assumptions is negative progress.

## The client asked me directly for a scope addition. What do I say?

"Good idea — let me get it costed." Nothing is agreed on a call. Additions go
through a written change order, priced by Theo. The kickoff out-of-scope list
exists precisely so this conversation is expected rather than awkward.

## When can I mark a status YELLOW?

The moment a risk needs a client decision to stay on schedule. Never soften a
YELLOW to GREEN — that exact move is documented in the Cobble & Crane retro
and it is the most expensive mistake in our history that didn't involve a
production incident.

## Who can declare a major incident?

Priya, or Maya in her absence (Automation Incident Response SOP). If you think
it's major, page Priya and say so; over-paging is free, under-paging isn't.

## What's our stance on fine-tuning?

Last resort, almost never. Retrieval over the client's documents solves the
"model doesn't know our business" problem cheaper, more transparently, and
with citations. If someone insists, the LLM Vendor Selection Playbook has the
cost framing that usually ends the conversation.

## Where do prompts live?

In the engagement repo, versioned, with the eval gate on every change. Never
in a dashboard textbox. See Prompt Engineering Standards.

## Can I reuse code between clients?

Patterns yes, client-specific code no. Anything generic enough to reuse gets
extracted into the internal library (Priya reviews) with no client references.
