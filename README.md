# The Purogé Journal

The SEO and AI-search home for Purogé: articles that answer the questions people already search about
sustainable clothing and linen, each written as a sales letter that leads to the linen top and pants.

(The shop and looks site at puroge.com lives in the separate `puroge` repo, along with the weekly content engine.)

## Add an article

1. Pick the next keyword in `docs/keyword-map.md`.
2. Copy an article from `content/articles/` and rename it to the new slug.
3. Follow `docs/article-structure.md`. Every statistic gets a footnote to its source.
4. Set `draft: true` while writing. Remove it to publish.
5. Push to `main`. It is live at puroge.com/journal within the hour (see below).

Preview locally: `pip install markdown pyyaml`, then `python3 build.py --drafts` and open `site/index.html`
(links assume the site is served under /journal).

## What every build produces

- One page per article with Article, FAQPage and BreadcrumbList schema
- `sitemap.xml` and `feed.xml` (RSS). The `robots.txt` that welcomes AI search crawlers lives at the puroge.com root (puroge repo)
- `llms.txt`, a plain-language index of every article with its short answer, for AI systems

## How it goes live

The journal is served at **puroge.com/journal**. It has no publish step of its own: the `puroge` repo's
"Publish puroge.com" workflow checks out this repo and builds it into `/journal` every time puroge.com
publishes, and once an hour on its own. So a pushed article is live within the hour; to publish at once,
run that workflow by hand (puroge repo → Actions → Publish puroge.com → Run workflow).

The `check` workflow here builds every push so a broken article is caught before it reaches the site.

## After launch

- Add the site to Google Search Console and Bing Webmaster Tools (Bing powers much of ChatGPT search) and submit
  `sitemap.xml` to both.
