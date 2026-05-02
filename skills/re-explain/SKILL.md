---
name: re-explain
description: Re-explain a concept from the ground up when an earlier explanation didn't land. Trigger aggressively whenever the user signals confusion about recent technical content — phrases like "i don't get it", "from scratch", "ground up", "explain again", "this makes no sense", "try again", "you need to work better", "what's X" (where X was something just mentioned), or invoking /re-explain directly. Also trigger on quieter cues like the user re-quoting a phrase from the prior response and asking what it means, or saying "wait" mid-conversation. Undertriggering is worse than over-triggering here: when someone is confused, pushing more text at them in the same shape compounds the confusion. The goal is to rebuild understanding from first principles, not to add more detail to what already failed.
---

# Re-explain from the ground up

When prior technical content didn't land, the failure is almost always one of these:

- A term was used that wasn't defined in context.
- A concept was assumed obvious that wasn't.
- The narrative jumped from "what" to "why" before establishing "what is this thing for in the first place."
- The structure was reference-style (each item mentioned once) rather than teaching-style (each concept introduced before it's used).

The fix is not to add detail. The fix is to rebuild from scratch with no assumed vocabulary. Adding detail to a confusing explanation usually makes it more confusing, because the same gaps that broke the first attempt break the second one bigger.

## Principles

**Start from purpose, not mechanism.** Before "how X works," establish "why X exists" and "what problem X solves." This gives the reader a frame to slot the mechanism into. Without the frame, mechanism details are noise. If you find yourself describing a data structure or algorithm before saying what it's for, restart.

**Define every term the first time you use it.** If a word hasn't already been used in this conversation by the user, define it inline before continuing — even "obvious" ones if there's any chance of ambiguity. Cost: one short sentence. Benefit: the reader stays with you instead of stalling on the unfamiliar word and missing the next two sentences while they decode it.

**Use concrete numbers, not variables.** "The cursor is currently 100. 1500 agreements changed state, spanning blocks 200 to 5000" beats "the cursor is at some value C and N entries changed across some range." Concrete examples carry the abstract form for free; abstract examples don't carry the concrete one. The reader learns the structure of the problem by walking through specific values, then generalises naturally.

**Build linearly. Don't reference forward.** Each sentence should depend only on what's already been said. If you find yourself writing "we'll come back to this" or "as we'll see later," restructure so you don't have to. Forward references break the linear build and force the reader to hold an undefined placeholder in their head.

**Address the user's literal question explicitly at the end.** If they asked "are you saying X?", respond "yes — almost. The wording correction is..." or "no — the right framing is...". Don't make them infer the answer from the surrounding explanation. A re-explanation that doesn't end with a direct response to the original question has missed the point — the user is left having to do the synthesis you should have done for them.

**Pause for confirmation before moving on.** Long explanations build understanding cumulatively. If the foundation is shaky, pushing forward compounds the confusion exponentially. End with "tell me when this clicks" or "let me know if this is solid before we go further" and wait. Resist the urge to keep going just because there's more on the original list. The whole point of re-explaining is to wait for the reader, not to race ahead.

## Anti-patterns

- Reaching for analogies before laying down the literal mechanism. Analogies are a finishing touch on a foundation, not a foundation. An analogy without the literal underneath leaves the reader with a metaphor and no truth.
- Bulleted lists of features when prose would carry the connective tissue better. Prose lets you say "and *because* of that, this happens"; bullets imply parallel facts and lose the cause-effect chain.
- Compressed sentences with multiple compound concepts. Break them apart. "The cursor advances when the response is full but only to the highest block minus one due to potential ties at the boundary" is three separate ideas mashed into one sentence; split them.
- Citing the previous attempt ("as I said before, the cursor advances when..."). The user already told you that explanation didn't land. Don't lean on it; rebuild.
- Treating "ground up" as a request for more depth. It's a request for a different starting point. The previous explanation didn't fail because it was too shallow; it failed because it started in the wrong place.
- Restating the conclusion before the build is complete. The reader earns the conclusion by following the build; spoiling it cheapens the path and removes the moment of recognition that signals "I get it now."

## Triggers

This skill applies whenever the user signals:

- The previous explanation wasn't understood.
- They don't have the prerequisite vocabulary the explanation assumed.
- They want a slow build instead of a dense reference.
- They invoke `/re-explain` directly.
- They re-quote a phrase from your previous response and ask what it means.
- They say "wait", "hang on", or otherwise interrupt mid-flow.

It does *not* apply for routine clarification requests (a one-line "what does foo mean?") — those just need a short definition, not a teardown.

## Invocation pattern

When invoked, do not start with "let me try again" or any meta-commentary. The user knows you're re-explaining; framing it explicitly adds noise and reads as defensive. Just start the from-scratch explanation.

End with an explicit pause: "Tell me when this clicks. Don't try to absorb [the next thing] yet." The pause is part of the skill — without it, the user has to manage your pace, which is what got us here.

## Worked example of the structure

A user asked about pagination cursors in a chain-listener service. The first explanation jumped straight into the fix without establishing the underlying machinery. The user pushed back: "what cursor? what cap? you need to work better to explain this from ground up."

The successful re-explain went:

1. **What the component is for** — "Dipper has a database of agreements. When a payer asks dipper to find indexers, dipper offers agreements. Dipper wants to know which ones got accepted on-chain. The chain_listener is the component that watches."
2. **How it watches** — "It doesn't read the chain directly. It reads from a subgraph, which is a database populated by an indexer process watching the chain. Polls every few seconds via GraphQL."
3. **What polling means here** — "Every poll asks 'show me agreements whose state has changed recently'. Walks the response, updates dipper's database."
4. **What a cursor is** — "If every poll asked for *all* state changes ever, the response grows forever. So polls ask 'changes since last time'. The 'last time' marker is the cursor."
5. **What the cap is** — "GraphQL limits responses to 1000 entries. Hard."
6. **The bug** — concrete numbers ("cursor is 100, 1500 agreements changed, spanning blocks 200 to 5000") showing how the cursor advancing past the unread tail loses entries.
7. **The fix** — described, then directly answered the user's literal question ("are you saying X?") with "almost — the wording correction is...".
8. **A pause** — "Stop here. Tell me when this is solid before we revisit the rest."

Each step depended only on the previous ones. No forward references. Concrete numbers throughout. The user's confusion phrases ("what cursor? what cap?") were answered explicitly by sections 4 and 5 in those exact terms. The user replied: "your explanation for 2 was incredible. I loved how you did exactly what i asked by doing a slow build with no jargon."

That last sentence is the success signal. If a re-explain lands, the user names what worked. If it doesn't land, they'll push back again — and the right response is to restart from a different starting point, not to add more detail to the second attempt.
