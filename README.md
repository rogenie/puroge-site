# The Purogé Journal

The SEO and AI-search home for Purogé: articles that answer the questions people already search about
sustainable clothing and linen, each written as a sales letter that leads to the linen top and pants.

(The shop and looks site at puroge.com lives in the separate `puroge` repo, along with the weekly content engine.)

## Add an article

1. Pick the next keyword in `docs/keyword-map.md`.
2. Copy an article from `content/articles/` and rename it to the new slug.
3. Follow `docs/article-structure.md`. Every statistic gets a footnote to its source.
4. Set `draft: true` while writing. Remove it to publish.
5. Push to `main`. GitHub Actions builds and publishes in about a minute.

Preview locally: `pip install markdown pyyaml`, then `python3 build.py --drafts` and open `site/index.html`
(or run `python3 -m http.server -d site` and set `base_path` to `""` in `site.json` while previewing).

## What every build produces

- One page per article with Article, FAQPage and BreadcrumbList schema
- `sitemap.xml`, `feed.xml` (RSS), `robots.txt` that welcomes Google, Bing and AI search crawlers
- `llms.txt`, a plain-language index of every article with its short answer, for AI systems

## Moving to a puroge.com address

The site currently publishes at `rogenie.github.io/puroge-site`. To serve it from your own domain
(for example `journal.puroge.com`):

1. Add a CNAME record for `journal` pointing to `rogenie.github.io` at your domain registrar.
2. In this repo: Settings → Pages → Custom domain → `journal.puroge.com`.
3. In `site.json`: set `base_url` to `https://journal.puroge.com` and `base_path` to `""`. Push.

## After launch

- Add the site to Google Search Console and Bing Webmaster Tools (Bing powers much of ChatGPT search) and submit
  `sitemap.xml` to both.
