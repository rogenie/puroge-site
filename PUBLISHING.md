# Purogé Journal: publishing runbook

This is Rogenie's runbook for the automatic publisher. Publishing is fully automatic by her choice:
no review, no approval step. Because nobody checks before it goes live, every rule here is mandatory.

The journal lives at **https://puroge.com/journal/**. Pushing to `main` here is enough: the puroge.com
publish workflow pulls this repo and rebuilds every hour, so a pushed article is live within the hour.

## Each run

1. Today = today's date in America/Los_Angeles.
2. Open `content/calendar.json`. **Due** = items dated today or earlier with `status` `"todo"`.
   Publish every due item, oldest first (a past date means a run was missed: catch it up).
   Never publish an item dated in the future. If nothing is due, do the topic top-up check (below) and stop.
3. Before writing, list `content/articles/` and read the titles. If the topic is already covered,
   set the item to `"skip"` with a `note` and move on.
4. Research (see Sources), write (see Writing), fact-check (see Fact-check).
5. Write the article to `content/articles/<slug>.md` with `date:` = today and `updated:` = today.
6. Run `pip install --break-system-packages -q markdown pyyaml` then `python3 build.py`.
   It must report one more article than before and `site/<slug>/index.html` must exist.
7. In `content/calendar.json` set the item's `status` to `"published"`, add `"url": "https://puroge.com/journal/<slug>/"`
   and `"published": "<today>"`. Keep the file's formatting (2-space indent, UTF-8).
8. Add the new slug to the `related:` list of 1-2 existing articles that it genuinely relates to.
9. Commit `content/` only (never commit `site/`), message `Publish: <title>`, author
   `Rogenie Cordero <rogenie@gmail.com>`. `git pull --rebase origin main`, then `git push origin main`.
   If refused, pull --rebase and push once more.

If an article can't stand without a fact you couldn't confirm, don't publish it: set `status` to `"held"`
with a `note` saying why, commit and push only that calendar change, and publish the next todo item instead.

## Sources

- Search with WebSearch (standard mode). WebFetch only URLs a search returned in this run.
- Prefer primary and authoritative sources: government agencies (EPA, FTC, USDA, NIH), research papers
  (journal sites, PubMed Central, Europe PMC), standards bodies (OEKO-TEX, GOTS, Textile Exchange),
  established organizations (Ellen MacArthur Foundation, IUCN, CFDA, UNEP), and major news outlets.
- Brand blogs and shops (including competitors) are acceptable only for styling or care tips, never for statistics.

## Fact-check (blocking)

- Every statistic, percentage, date, study detail or price must come from a page opened in this run, and be
  footnoted to it. Remove anything you can't confirm.
- Health: never claim a fabric causes or prevents illness. Microplastics in the body: say what studies found and
  that health effects are still being studied. No medical advice.
- Never invent quotes, customers, testimonials, reviews, statistics or personal experiences of Rogenie.
- Do not mention or promote "the Purogé label", its products, prices or pre-orders. Rogenie will update this
  runbook when that is ready. Link to the curated edit on puroge.com only through the `cta` block.
- Copy rules: quotes from any source under 15 words and at most one per source; otherwise paraphrase.

## Writing

Follow `docs/article-structure.md` exactly (Sam Ovens sales-letter structure, 14 parts, in the Purogé voice)
and copy the front-matter shape of an existing article in `content/articles/`.

- Reader: upper-middle-class women and men who buy fewer, better pieces and wear high-end, high-quality clothing.
  Considered, not flashy. They travel, work in client-facing roles and care what touches their skin.
- Voice: warm, exacting, a little dry. Teach a reason, not a vibe. Name the material. Never shame what people own.
  Never write "look rich", "classy vs. trashy", "elevate your wardrobe", "game-changer" or "in today's world".
- `quick_answer`: 40-60 words that fully answer the primary keyword. Headings phrased as questions where natural.
- 1,000-1,600 words of body. 4-6 FAQ entries that real people search. Footnotes for every source.
- `primary_keyword` in the title, the slug and the quick answer. `related:` lists 2-3 existing slugs, always
  including `why-humans-should-wear-sustainable-clothing`.
- `cta` buttons: `work` and/or `travel` links (see site.json `shop_links`).
- Quote any front-matter value that contains a colon.

## Topic top-up

If fewer than 6 items remain with `status` `"todo"`, add new items so there are 10, dated on the calendar's
cadence (Monday, Wednesday, Friday) after the last dated item. Choose questions people actually search about
natural fiber, linen, sustainable clothing, fabric care, dressing for work and travel, found through this run's
searches ("people also ask" style questions, forum threads, competitor FAQ pages). Each item:
`{"date", "slug", "title", "primary_keyword", "angle", "status": "todo"}`. Never repeat an existing topic.
Also append them to the queue in `docs/keyword-map.md`.

## Never

- Never edit `build.py`, `static/`, `site.json` or the workflows.
- Never publish more than the due items, and never backdate.
- Never stop to ask for permission. If something blocks a due article (fetch refused, build failing, push
  refused twice), send a push notification naming the article, the step and the exact error.
