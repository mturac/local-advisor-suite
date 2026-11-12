# The Outside View

Kahneman's finding, and the most robust one in judgment research: when predicting
the outcome of a plan, people instinctively reason from the inside — the plan's
own details, its specific merits, how well it is put together. The inside view is
where optimism lives. The outside view asks a different question first: **what
happened to everyone else who tried this?** The reference class answer is usually
closer to the truth than the plan's own story, because plans are systematically
better written than executed.

## The three steps

1. **Pick the reference class.** Not "companies like ours" — too broad. Not
   "this exact project" — that is the inside view wearing a costume. The class
   is the set of attempts similar in the way that matters for outcome:
   "second rewrite attempts of monolith services", "first B2B tool adoptions
   by a team under 10", "microservices migrations at companies without a
   platform team". Name the similarity dimension out loud.

2. **Find the base rate.** What fraction of the class succeeded? Sources vary
   in quality: industry surveys, public postmortems, your own history, or a
   reasoned estimate when nothing better exists. An honest range is fine;
   record the number you actually believe, as a percentage.

3. **Argue the adjustment — or refuse it.** The plan proceeds on the inside
   view only if this attempt differs from the class in a way that plausibly
   changes the odds. "We will be more disciplined" is not an adjustment; it is
   what every member of the class believed. Real adjustments are checkable:
   "we have done this exact migration twice before, both under budget" or
   "the class failed on a regulator that we have already cleared in writing".

## The mechanical rule in this suite

```
$WB devil-outside --reference-class "..." --base-rate 30 --adjustment "none"
```

A base rate of **50% or worse with no argued adjustment** auto-opens a SERIOUS
challenge: *the plan assumes this case beats the reference class*. That
assumption now needs a rebuttal like any other — with a basis, on the record —
or it keeps the verdict at PROCEED_WITH_GUARDS even if every hand-written
challenge was answered. Optimism must be argued, not assumed.

With `--adjustment "..."` the flag is not raised: you have made the inside-view
claim explicitly, and the record shows what it rests on. The rebuttal basis
"constraint: we have a signed pilot commitment" and the adjustment "we have a
signed pilot commitment" are the same claim in two places — write it once,
properly.

## Common reference classes and their sobering rates

Use these as priors when you have nothing better, and replace them with
measured numbers when you do: large software projects are more often late,
over budget, or cancelled than not; enterprise tool adoptions frequently fall
back to the previous tool within two years; first hires at companies under
ten people fail more often than they stick; and process changes usually decay
back to the old way unless someone owns them. The exact numbers are yours to
find — the point is that "most attempts like this do not end the way the plan
says" is the default hypothesis, not the pessimistic one.

## When the outside view is wrong

Sometimes the class is genuinely irrelevant: you are not like the class in a
measurable way, or the class's failure cause is structurally absent here.
That is exactly what the adjustment field is for. The discipline is not
"always obey the base rate" — it is "the base rate is the opening bid, and
beating it requires evidence, not confidence".
