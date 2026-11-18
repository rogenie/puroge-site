#!/usr/bin/env python3
"""Build the Purogé Journal into ./site.

Each article is one Markdown file in content/articles/ with YAML front matter.
Run `python3 build.py` (add --drafts to include drafts), then open site/index.html.
"""
import html
import json
import math
import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).parent
OUT = ROOT / "site"
SITE = json.loads((ROOT / "site.json").read_text())
INCLUDE_DRAFTS = "--drafts" in sys.argv

REQUIRED = ["title", "slug", "description", "date", "quick_answer", "primary_keyword"]


def url(path=""):
    """Root-relative link that respects base_path (for GitHub Pages project sites)."""
    return f"{SITE['base_path']}/{path.lstrip('/')}"


def abs_url(path=""):
    return f"{SITE['base_url']}/{path.lstrip('/')}"


def esc(s):
    return html.escape(str(s), quote=True)


def fmt_date(d):
    return d.strftime("%B %-d, %Y")


def load_articles():
    articles = []
    for f in sorted((ROOT / "content" / "articles").glob("*.md")):
        raw = f.read_text()
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
        if not m:
            sys.exit(f"{f.name}: missing front matter")
        meta = yaml.safe_load(m.group(1))
        missing = [k for k in REQUIRED if not meta.get(k)]
        if missing:
            sys.exit(f"{f.name}: missing {', '.join(missing)}")
        if meta.get("draft") and not INCLUDE_DRAFTS:
            continue
        for k in ("date", "updated"):
            if isinstance(meta.get(k), str):
                meta[k] = datetime.strptime(meta[k], "%Y-%m-%d").date()
        meta.setdefault("updated", meta["date"])
        md = markdown.Markdown(
            extensions=["footnotes", "toc", "attr_list", "md_in_html", "tables", "smarty"],
            extension_configs={
                "footnotes": {"BACKLINK_TEXT": "↩", "SEPARATOR": "-"},
                "toc": {"toc_depth": "2"},
            },
        )
        body = md.convert(m.group(2))
        notes = ""
        if '<div class="footnote">' in body:
            body, notes = body.split('<div class="footnote">', 1)
            notes = '<div class="footnote">' + notes
        meta["html"] = body
        meta["notes"] = notes
        meta["toc"] = md.toc_tokens
        words = len(re.sub(r"<[^>]+>", " ", body).split())
        meta["minutes"] = max(1, math.ceil(words / 230))
        meta["words"] = words
        articles.append(meta)
    articles.sort(key=lambda a: (a.get("order", 99), -a["date"].toordinal()))
    return articles


FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500'
    '&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">'
)


def org_schema():
    return {
        "@type": "Organization",
        "@id": abs_url("#org"),
        "name": SITE["name"],
        "url": SITE["shop_url"],
        "description": SITE["description"],
    }


def page(title, description, path, body, schema=None, og_type="website", extra_head=""):
    graph = [org_schema(), {
        "@type": "WebSite", "@id": abs_url("#site"), "name": SITE["journal_name"],
        "url": abs_url(), "publisher": {"@id": abs_url("#org")},
    }] + (schema or [])
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
    canonical = abs_url(path)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{esc(SITE['journal_name'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="{SITE['locale']}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f5efe4">
<link rel="alternate" type="application/rss+xml" title="{esc(SITE['journal_name'])}" href="{url('feed.xml')}">
<link rel="icon" href="{url('static/favicon.svg')}" type="image/svg+xml">
{FONTS}
<link rel="stylesheet" href="{url('static/style.css')}">
{extra_head}
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead">
  <div class="wrap bar">
    <a class="brand" href="{url()}">Purogé<span>Journal</span></a>
    <nav aria-label="Main">
      <a href="{url()}">Articles</a>
      <a href="{url('about/')}">About</a>
      <a class="shop" href="{SITE['shop_url']}">Shop the edit</a>
    </nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="foot">
  <div class="wrap">
    <p class="foot-brand">Purogé</p>
    <p class="foot-ded">{esc(SITE['dedication'])}</p>
    <p class="foot-links"><a href="{url()}">Journal</a> · <a href="{url('about/')}">About</a> · <a href="{SITE['shop_url']}">puroge.com</a> · <a href="{url('feed.xml')}">RSS</a></p>
    <p class="foot-small">© {date.today().year} Purogé. Some shop links may earn a commission at no cost to you.</p>
  </div>
</footer>
</body>
</html>
"""


def byline(a):
    upd = ""
    if a["updated"] != a["date"]:
        upd = f' · Updated <time datetime="{a["updated"].isoformat()}">{fmt_date(a["updated"])}</time>'
    return (f'<p class="byline">By <span class="author">{esc(SITE["author"]["name"])}</span>, '
            f'{esc(SITE["author"]["role"])} · <time datetime="{a["date"].isoformat()}">{fmt_date(a["date"])}</time>'
            f'{upd} · {a["minutes"]} min read</p>')


def toc_html(a):
    items = [t for t in a["toc"] if t["level"] == 2 and not t["id"].startswith("sources")]
    if len(items) < 3:
        return ""
    lis = "".join(f'<li><a href="#{t["id"]}">{esc(html.unescape(t["name"]))}</a></li>' for t in items)
    return f'<nav class="toc" aria-label="In this article"><p class="label">In this article</p><ol>{lis}</ol></nav>'


def faq_html(a):
    faqs = a.get("faq") or []
    if not faqs:
        return ""
    items = "".join(
        f'<details class="q"><summary><h3>{esc(f["q"])}</h3></summary>'
        f'<div class="a">{markdown.markdown(f["a"], extensions=["smarty"])}</div></details>'
        for f in faqs)
    return f'<section class="faq" id="questions"><h2>Questions people ask</h2>{items}</section>'


def cta_html(a):
    c = a.get("cta")
    if not c:
        return ""
    btns = "".join(
        f'<a class="btn{" ghost" if i else ""}" href="{esc(SITE["shop_links"].get(b["link"], b["link"]))}">{esc(b["label"])}</a>'
        for i, b in enumerate(c["buttons"]))
    return (f'<aside class="cta"><p class="label">{esc(c.get("eyebrow", "The edit"))}</p>'
            f'<h2 class="cta-h">{esc(c["headline"])}</h2><p>{esc(c["text"])}</p>'
            f'<div class="btns">{btns}</div></aside>')


def related_html(a, articles):
    others = [o for o in articles if o["slug"] != a["slug"]]
    wanted = a.get("related") or []
    others.sort(key=lambda o: (o["slug"] not in wanted, o.get("order", 99)))
    others = others[:3]
    if not others:
        return ""
    cards = "".join(card(o) for o in others)
    return f'<section class="related"><p class="label">Keep reading</p><div class="grid">{cards}</div></section>'


def card(o, big=False):
    return (f'<a class="card{" big" if big else ""}" href="{url(o["slug"] + "/")}">'
            f'<span class="label">{esc(o.get("eyebrow", ""))}</span>'
            f'<span class="t">{esc(o["title"])}</span>'
            f'<span class="d">{esc(o["description"])}</span>'
            f'<span class="more">Read · {o["minutes"]} min</span></a>')


def article_page(a, articles):
    path = a["slug"] + "/"
    faq_schema = []
    if a.get("faq"):
        faq_schema = [{
            "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": f["q"],
                            "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in a["faq"]],
        }]
    schema = [{
        "@type": "Article",
        "@id": abs_url(path + "#article"),
        "headline": a["title"],
        "description": a["description"],
        "abstract": a["quick_answer"].strip(),
        "datePublished": a["date"].isoformat(),
        "dateModified": a["updated"].isoformat(),
        "wordCount": a["words"],
        "keywords": ", ".join([a["primary_keyword"]] + (a.get("keywords") or [])),
        "inLanguage": "en",
        "mainEntityOfPage": abs_url(path),
        "author": {"@type": "Person", "name": SITE["author"]["name"], "jobTitle": SITE["author"]["role"],
                   "worksFor": {"@id": abs_url("#org")}},
        "publisher": {"@id": abs_url("#org")},
        "citation": a.get("sources") or [],
    }, {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Journal", "item": abs_url()},
            {"@type": "ListItem", "position": 2, "name": a["title"], "item": abs_url(path)},
        ],
    }] + faq_schema
    body = f"""
<article class="article">
  <header class="art-head wrap narrow">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{url()}">Journal</a> <span>/</span> {esc(a.get('eyebrow', ''))}</nav>
    <p class="eyebrow">{esc(a.get('eyebrow', ''))}</p>
    <h1>{esc(a['title'])}</h1>
    <p class="dek">{esc(a.get('subhead', ''))}</p>
    {byline(a)}
  </header>
  <div class="wrap narrow">
    <section class="answer" aria-label="Short answer">
      <p class="label">The short answer</p>
      <p>{esc(a['quick_answer'].strip())}</p>
    </section>
    {toc_html(a)}
    <div class="prose">
{a['html']}
    </div>
    {faq_html(a)}
    {cta_html(a)}
    <aside class="author-box">
      <p class="label">About the author</p>
      <p><strong>{esc(SITE['author']['name'])}</strong> — {esc(SITE['author']['bio'])}</p>
    </aside>
    <section class="sources" id="sources">{a['notes']}</section>
    {related_html(a, articles)}
  </div>
</article>
"""
    title = a.get("seo_title") or f"{a['title']} | Purogé"
    return page(title, a["description"], path, body, schema, og_type="article",
                extra_head=f'<meta property="article:published_time" content="{a["date"].isoformat()}">'
                           f'<meta property="article:modified_time" content="{a["updated"].isoformat()}">')


def index_page(articles):
    feat = articles[0] if articles else None
    rest = articles[1:]
    feat_html = card(feat, big=True) if feat else '<p class="empty">The first article is on its way.</p>'
    grid = f'<div class="grid">{"".join(card(o) for o in rest)}</div>' if rest else ""
    schema = [{
        "@type": "CollectionPage", "name": SITE["journal_name"], "url": abs_url(),
        "hasPart": [{"@type": "Article", "headline": o["title"], "url": abs_url(o["slug"] + "/")} for o in articles],
    }]
    body = f"""
<section class="hero wrap">
  <p class="eyebrow">{esc(SITE['journal_name'])}</p>
  <h1 class="hero-h">Wear plants, not plastic.</h1>
  <p class="hero-dek">Most of what’s in a modern closet is made from oil. We explain, with sources, why natural fiber is better for the body that wears it and the world that makes it, and how to wear linen well at work and on the road.</p>
</section>
<section class="wrap list">
  {feat_html}
  {grid}
</section>
"""
    return page(f"{SITE['journal_name']} — Why Natural-Fiber Clothing Matters", SITE["description"], "", body, schema)


def about_page():
    body = f"""
<article class="article">
  <header class="art-head wrap narrow">
    <p class="eyebrow">About</p>
    <h1>Fewer pieces. Better fiber. Worn for years.</h1>
    <p class="dek">{esc(SITE['dedication'])}</p>
  </header>
  <div class="wrap narrow prose">
    <p>Purogé curates clothing for people who would rather buy once and buy well. We start from the fabric: what it is made of, how it feels against the skin, and how long it will last. Our edit centers on two pieces that do most of the work in a considered wardrobe: a linen top and a comfortable pair of pants, both made for the office and the airport.</p>
    <p>This journal is where we explain our reasoning. Every statistic links to its source. When the evidence is uncertain, we say so.</p>
    <p><a class="btn" href="{SITE['shop_url']}">Visit puroge.com</a></p>
  </div>
</article>
"""
    schema = [{"@type": "AboutPage", "name": "About Purogé", "url": abs_url("about/")}]
    return page("About Purogé", SITE["description"], "about/", body, schema)


def write(rel, text):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def main():
    articles = load_articles()
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT / "static")
    write("index.html", index_page(articles))
    write("about/index.html", about_page())
    for a in articles:
        write(f"{a['slug']}/index.html", article_page(a, articles))
    write("404.html", page("Page not found | Purogé", SITE["description"], "404.html",
                           f'<section class="hero wrap"><h1 class="hero-h">Not here.</h1>'
                           f'<p class="hero-dek"><a href="{url()}">Back to the journal</a></p></section>'))

    # sitemap
    today = date.today().isoformat()
    urls = [(abs_url(), today), (abs_url("about/"), today)] + \
           [(abs_url(a["slug"] + "/"), a["updated"].isoformat()) for a in articles]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n")

    # robots: welcome search and AI answer engines
    write("robots.txt", "User-agent: *\nAllow: /\n\n"
          "# AI search and answer engines are welcome to read and cite this journal.\n"
          + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in
                    ["Googlebot", "Bingbot", "OAI-SearchBot", "ChatGPT-User", "GPTBot", "PerplexityBot",
                     "Perplexity-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "Applebot", "Google-Extended"])
          + f"Sitemap: {abs_url('sitemap.xml')}\n")

    # llms.txt: a plain-language map for AI systems
    lines = [f"# {SITE['journal_name']}", "", f"> {SITE['description']}", "",
             f"Shop: {SITE['shop_url']}", "", "## Articles", ""]
    for a in articles:
        lines.append(f"- [{a['title']}]({abs_url(a['slug'] + '/')}): {a['quick_answer'].strip()}")
    write("llms.txt", "\n".join(lines) + "\n")

    # RSS
    items = "".join(
        f"<item><title>{esc(a['title'])}</title><link>{abs_url(a['slug'] + '/')}</link>"
        f"<guid>{abs_url(a['slug'] + '/')}</guid><pubDate>{a['date'].strftime('%a, %d %b %Y 08:00:00 -0800')}</pubDate>"
        f"<description>{esc(a['description'])}</description></item>" for a in articles)
    write("feed.xml", f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>'
          f"<title>{esc(SITE['journal_name'])}</title><link>{abs_url()}</link>"
          f"<description>{esc(SITE['description'])}</description>{items}</channel></rss>")
    write(".nojekyll", "")
    print(f"Built {len(articles)} article(s) into {OUT}")


if __name__ == "__main__":
    main()
