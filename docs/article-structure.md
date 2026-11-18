# Article structure (Sam Ovens sales-copy style, in the Purogé voice)

Every article is a sales letter in disguise: it answers the search question completely, then moves the reader
from "I'm curious" to "I want the right piece." Follow this order.

| # | Section | What it does | Where it lives |
|---|---|---|---|
| 1 | **Eyebrow + headline** | The exact search question, stated plainly | `eyebrow`, `title` |
| 2 | **Subhead** | The promise: what they'll know by the end | `subhead` |
| 3 | **Short answer** | 40–60 word direct answer, for Google and AI to quote | `quick_answer` |
| 4 | **"Read this if…"** | Call out the reader and their exact frustration | first `##` |
| 5 | **The problem** | Name what's actually wrong | `##` |
| 6 | **Agitate** | Make it real, with sourced numbers | `##` + footnotes |
| 7 | **It isn't your fault** | Shift blame to the system; lift guilt | `##` |
| 8 | **The new way (named rule)** | One memorable rule or test | `<div class="rule">` |
| 9 | **Proof / mechanism** | Why the new way works, with sources | `##` + footnotes |
| 10 | **The offer** | The linen top and pants, tied to the reader's situation | `##` + `cta` |
| 11 | **Who it's not for** | Disqualify; builds trust | `##` |
| 12 | **Objections** | Real questions people search | `faq` (becomes FAQ schema) |
| 13 | **Call to action** | One clear next step | `cta` |
| 14 | **P.S.** | Restate the single most important idea | `<p class="ps">` |

## Voice rules (from the brand book)

- Warm, exacting, a little dry. Teach a reason, not a vibe.
- Name the material of every piece.
- Never shame what people already own. Never say "look rich" or "classy vs. trashy."
- Short sentences. One idea per line.
- Honest about evidence: if research is early or uncertain, say so.

## Building blocks

```html
<div class="rule" markdown="1">
<p class="label">The fiber rule</p>

One sentence the reader will remember.
</div>

<div class="callout" markdown="1">
<p class="label">Label</p>

A side note, example or calculation.
</div>

> A pull quote (renders large, italic, oxblood).

<p class="ps"><strong>P.S.</strong> The closing line.</p>
```

Sources go in Markdown footnotes (`[^name]`) and also in the `sources:` list in front matter.
