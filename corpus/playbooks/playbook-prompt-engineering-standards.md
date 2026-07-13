---
title: "Playbook: Prompt Engineering Standards"
doc_type: playbook
tags: [prompts, llm, standards]
---

# Playbook: Prompt Engineering Standards

Owner: Sam Alvarez. House rules for every prompt that ships in a client
system. Prompts are code: versioned, reviewed, and tested like code.

## Structure standards

- **System prompts state the refusal behavior explicitly.** Every grounded
  assistant's system prompt includes: answer only from the provided context,
  cite sources for every claim, and say "I don't have that in the knowledge
  base" when the context is insufficient. The refusal wording is part of the
  client's approved copy.
- **Context blocks are delimited and labeled.** Retrieved chunks arrive in
  clearly marked blocks with their source path and heading, so citations can
  point at real locations.
- **One prompt, one job.** A prompt that classifies *and* extracts *and*
  summarizes does all three badly. Chain small prompts instead.

## Change control

- Prompts live in the repo, not in a dashboard textbox. Every change is a
  commit with a reason.
- Any prompt change on a shipped system triggers the eval set before deploy —
  the same gate as a code change (see RAG Implementation Playbook). Tidewater's
  eval caught a "helpful" prompt tweak that doubled unsupported claims; the
  tweak never shipped.

## Anti-patterns we reject

- **Begging ("please please only use the context")** — restructure the prompt
  instead; repetition is not control.
- **Threats and roleplay pressure** — unprofessional in client systems, and
  brittle.
- **Hidden instructions in retrieved content** — retrieval output is data, not
  instructions. Our standard template tells the model exactly that, and the
  eval set includes an injection probe to verify it holds.

## Review checklist (before any prompt merges)

1. Does it state the grounding/refusal rule?
2. Are context and instructions clearly separated?
3. Is there an eval case that would catch this prompt regressing?
4. Would you be comfortable if the client read it? (They own it at handoff.)
