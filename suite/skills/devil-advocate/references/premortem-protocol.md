# Premortem Protocol

The premortem is Gary Klein's technique, and its power is not mystical: it is the only
reliably demonstrated way to get people to voice doubts they already have. Asking
"what might go wrong" gets polite hedging. Asking "it failed — tell me why" gets
causes, because failure is already assumed and defending the plan is pointless. In
Klein's trials the premortem raised the identified risk count by roughly 30% over
standard brainstorming — not because the risks were new, but because people finally
said them.

## The rules that make it work

1. **Write it in past tense, as history.** "The migration stalled in cutover week
   when..." — not "the migration might stall if...". The tense is the technique:
   it removes the social cost of pessimism.

2. **No hedging words.** "Unforeseen difficulties", "various challenges", "resource
   constraints" are placeholders, not causes. A cause is specific enough that
   someone could go check whether it is already forming: "the billing adapter was
   never rewritten and its owner left in March" is a cause.

3. **At least one cause must be uncomfortable.** If every cause is external
   (vendor, market, timing) and none is about the team, the plan, or the estimate,
   the premortem was theater. The most common real cause is "we underestimated X",
   and X is almost always internal.

4. **One premortem per session.** A second story is a rewrite of the first, not
   fresh divergence. If the plan changes materially, open a new session.

## How to run it in this suite

Run it after `devil-open` and **before** the challenges. The order matters:
the premortem primes what you look for; challenges written first anchor you to
defending or attacking a specific list, and the premortem then only confirms
what you already wrote.

```
$WB devil-premortem \
  --failure-story "Twelve months on, the tool adoption failed: the team still
   routes real work through the old system, the license lapsed, and the
   integration branch was deleted unreleased." \
  --cause "no owner was named for the 90-day adoption push" \
  --cause "the promised connector did not cover our invoice edge cases" \
  --cause "training was one demo, not a migration path"
```

Each cause then becomes either a `devil-challenge` (with the cause as the
assumption under attack) or an answer that closes it. The premortem's job is to
surface the causes; the challenge ledger's job is to decide whether they sink
the plan.

## The three standard prompts

When the failure story does not come easily, use the archetype prompts from
`devil-plan` — each archetype carries three. For a build: "it shipped late and
over budget — which underestimated part ate the calendar?" For a launch: "it
landed and nobody came — where did the audience assumption break?" For a hire:
"90 days in and it is not working — what did the interviews never test?"

## What a bad premortem looks like

- A list of generic risks ("competition", "regulation") with no mechanism —
  a cause names the chain, not the category.
- Causes that are all one type (all technical, all external, all market) —
  real failures are usually a compound of one estimate error plus one
  coordination error.
- A story where the plan itself was perfect and the world betrayed it. It
  happens; far less often than the story suggests.
