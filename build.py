#!/usr/bin/env python3
"""Build the Purogé Journal into ./site.

Each article is one Markdown file in content/articles/ with YAML front matter.
Run `python3 build.py` (add --drafts to include drafts). puroge.com's publish step runs
`python3 build.py --out <puroge site>/journal`, so the journal goes live at puroge.com/journal.
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
OUT = Path(sys.argv[sys.argv.index("--out") + 1]).resolve() if "--out" in sys.argv else ROOT / "site"
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


EMBLEM = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" aria-hidden="true" focusable="false">\n<circle cx="50" cy="50" r="49" fill="#6b2a26"/>\n<circle cx="50" cy="50" r="42" fill="none" stroke="#f6f1e8" stroke-width="1" stroke-dasharray="3.2 2.4" opacity=".75"/>\n<g fill="#f6f1e8" transform="translate(30.04 74.00) scale(0.0732 -0.0732)"><path d="M208 85Q208 55 215.0 39.5Q222 24 244.5 18.0Q267 12 312 12Q315 12 315.0 6.0Q315 0 312 0Q280 0 242.5 1.0Q205 2 161 2Q126 2 94.0 1.0Q62 0 37 0Q34 0 34.0 6.0Q34 12 37 12Q70 12 86.0 17.0Q102 22 107.5 37.0Q113 52 113 81V544Q113 573 107.5 587.5Q102 602 86.0 607.5Q70 613 37 613Q34 613 34.0 619.0Q34 625 37 625Q62 625 93.5 623.5Q125 622 160 622Q184 622 222.5 625.0Q261 628 297 628Q358 628 405.5 611.5Q453 595 481.0 559.0Q509 523 511 464Q512 412 493.0 374.0Q474 336 441.5 311.5Q409 287 370.0 274.5Q331 262 292 262Q281 262 268.5 263.0Q256 264 244 267Q241 268 242 275Q243 279 245 280Q246 280 247 280Q255 278 265.0 277.0Q275 276 282 276Q315 276 343.0 294.0Q371 312 388.5 349.0Q406 386 406 442Q406 495 389.0 532.0Q372 569 341.5 588.5Q311 608 267 608Q244 608 231.0 603.5Q218 599 213.0 585.0Q208 571 208 542Z"/></g>\n</svg>'

LOGO = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 -10 4974 865" aria-hidden="true" focusable="false"><g fill="currentColor" transform="translate(0 815) scale(1 -1)"><path transform="translate(0 0)" d="M200 85Q200 55 207.5 39.5Q215 24 239.0 18.0Q263 12 311 12Q314 12 314.0 6.0Q314 0 311 0Q279 0 241.5 1.0Q204 2 160 2Q127 2 95.5 1.0Q64 0 39 0Q37 0 37.0 6.0Q37 12 39 12Q74 12 91.5 17.0Q109 22 114.5 37.0Q120 52 120 81V544Q120 573 114.5 587.5Q109 602 91.5 607.5Q74 613 39 613Q37 613 37.0 619.0Q37 625 39 625Q64 625 95.0 623.5Q126 622 159 622Q185 622 222.5 625.0Q260 628 298 628Q356 628 402.5 611.0Q449 594 477.0 558.0Q505 522 506 464Q506 412 487.0 374.0Q468 336 435.5 311.0Q403 286 363.5 274.0Q324 262 286 262Q274 262 261.5 263.0Q249 264 238 267Q234 268 236 275Q237 280 239 280Q239 280 240 280Q249 278 258.5 277.0Q268 276 275 276Q313 276 345.0 294.0Q377 312 397.0 349.5Q417 387 417 443Q417 497 398.5 534.0Q380 571 347.0 591.0Q314 611 271 611Q243 611 227.5 607.0Q212 603 206.0 588.0Q200 573 200 542Z"/><path transform="translate(746 0)" d="M572 510Q572 560 549.5 586.5Q527 613 483 613Q480 613 480.0 619.0Q480 625 483 625Q506 625 531.0 623.5Q556 622 585 622Q610 622 634.5 623.5Q659 625 680 625Q682 625 682.0 619.0Q682 613 680 613Q640 613 619.5 586.5Q599 560 599 510V227Q599 152 569.0 98.0Q539 44 485.0 15.5Q431 -13 359 -13Q285 -13 229.0 15.5Q173 44 142.0 97.0Q111 150 111 223V544Q111 573 105.0 587.5Q99 602 81.5 607.5Q64 613 30 613Q27 613 27.0 619.0Q27 625 30 625Q55 625 85.0 623.5Q115 622 150 622Q186 622 216.5 623.5Q247 625 270 625Q273 625 273.0 619.0Q273 613 270 613Q236 613 218.5 607.0Q201 601 195.5 586.0Q190 571 190 542V258Q190 138 242.0 78.5Q294 19 386 19Q474 19 523.0 73.5Q572 128 572 226Z"/><path transform="translate(1646 0)" d="M546 0Q530 0 493.5 38.5Q457 77 406 149Q358 216 298 308Q276 304 253 304Q241 304 228.0 304.5Q215 305 204 306V81Q204 52 209.5 37.0Q215 22 232.5 17.0Q250 12 285 12Q288 12 288.0 6.0Q288 0 285 0Q260 0 230.0 1.0Q200 2 164 2Q130 2 99.0 1.0Q68 0 43 0Q40 0 40.0 6.0Q40 12 43 12Q77 12 94.5 17.0Q112 22 118.5 37.0Q125 52 125 81V544Q125 573 119.0 587.5Q113 602 96.0 607.5Q79 613 44 613Q42 613 42.0 619.0Q42 625 44 625Q69 625 99.5 623.5Q130 622 164 622Q196 622 236.0 625.0Q276 628 306 628Q390 628 434.5 592.5Q479 557 479 498Q479 442 447 398Q416 355 365 330Q444 216 501 147Q559 75 604.0 43.5Q649 12 690 12Q693 12 693.0 6.0Q693 0 690 0ZM397 466Q397 522 382.0 553.5Q367 585 339.5 598.0Q312 611 275 611Q237 611 220.5 597.5Q204 584 204 542V331Q218 330 234.5 329.0Q251 328 263 328Q337 328 367.0 362.0Q397 396 397 466Z"/><path transform="translate(2527 0)" d="M366 -12Q294 -12 235.5 13.5Q177 39 135.5 84.0Q94 129 71.5 187.5Q49 246 49 312Q49 393 80.5 454.0Q112 515 164.0 555.5Q216 596 278.0 616.0Q340 636 401 636Q475 636 533.5 609.5Q592 583 633.0 538.0Q674 493 695.5 436.0Q717 379 717 319Q717 249 689.0 189.0Q661 129 612.5 84.0Q564 39 500.5 13.5Q437 -12 366 -12ZM401 10Q464 10 515.5 42.5Q567 75 596.5 137.5Q626 200 626 291Q626 384 593.5 456.5Q561 529 501.5 570.5Q442 612 360 612Q255 612 197.5 541.0Q140 470 140 347Q140 276 158.5 214.5Q177 153 212.0 107.0Q247 61 295.0 35.5Q343 10 401 10Z"/><path transform="translate(3493 0)" d="M412 -12Q326 -12 258.5 13.5Q191 39 144.5 84.0Q98 129 73.5 188.0Q49 247 49 313Q49 388 77.5 447.0Q106 506 158.0 548.5Q210 591 279.0 613.5Q348 636 429 636Q481 636 527.5 627.0Q574 618 605 601Q614 597 615.0 594.0Q616 591 617 578L630 454Q630 451 625.0 450.0Q620 449 618 453Q608 484 591.0 513.5Q574 543 548.0 566.5Q522 590 486.5 604.0Q451 618 404 618Q330 618 270.0 583.5Q210 549 175.0 484.5Q140 420 140 330Q140 266 159.5 207.0Q179 148 217.0 102.0Q255 56 310.5 29.5Q366 3 438 3Q483 3 509.5 14.5Q536 26 548.0 52.5Q560 79 560 125Q560 173 554.0 195.5Q548 218 525.0 225.0Q502 232 450 232Q444 232 444.0 240.0Q444 248 449 248Q515 244 568.5 243.5Q622 243 680 246Q685 246 685.0 239.0Q685 232 680 232Q659 233 649.0 225.5Q639 218 636.5 193.0Q634 168 634 115Q634 82 636.0 66.0Q638 50 639.5 42.5Q641 35 641 27Q641 21 639.0 19.0Q637 17 630 15Q578 4 520.5 -4.0Q463 -12 412 -12Z"/><path transform="translate(4412 0)" d="M469 0H43Q40 0 40.0 6.0Q40 12 43 12Q77 12 94.5 17.0Q112 22 118.0 37.0Q124 52 124 81V544Q124 573 118.0 587.5Q112 602 94.5 607.5Q77 613 43 613Q40 613 40.0 619.0Q40 625 43 625H451Q461 625 461 616L463 490Q463 487 457.5 486.5Q452 486 451 489Q444 544 412.0 572.5Q380 601 328 601H277Q247 601 231.0 596.0Q215 591 209.0 577.5Q203 564 203 540V337H313Q364 337 388.0 354.5Q412 372 412 409Q412 411 417.5 411.0Q423 411 423 409Q423 378 422.5 361.0Q422 344 422 325Q422 302 423.5 279.0Q425 256 425 230Q425 228 419.0 228.0Q413 228 413 230Q413 273 388.5 293.5Q364 314 310 314H203V85Q203 61 208.5 47.5Q214 34 229.0 28.5Q244 23 271 23H337Q394 23 431.0 56.5Q468 90 482 152Q482 153 482 153Q483 155 488 154Q494 153 494 150Q490 123 487.0 85.0Q484 47 484 15Q484 0 469 0Z"/></g><g transform="translate(0 815)"><path d="M4677 -687 L4739 -783" style="stroke:var(--accent)" stroke-width="38" stroke-linecap="round" fill="none"/></g></svg>'

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
    <a class="brand" href="/" aria-label="Purogé home"><span class="emb">{EMBLEM}</span>{LOGO}<span>Journal</span></a>
    <nav aria-label="Main">
      <a href="/looks/">Looks</a>
      <a href="/#label"><span class="nav-the">The </span>Label</a>
      <a class="nav-story" href="/story/">Story</a>
      <a class="here" href="{url()}" aria-current="page">Journal</a>
    </nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="foot">
  <div class="wrap">
    <p class="foot-brand">{LOGO}</p><p class="foot-tag">{esc(SITE["tagline_brand"])}</p>
    <p class="foot-ded"><a href="https://puroge.com/story/">{esc(SITE['dedication'])}</a></p>
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
  <h1 class="hero-h">The case for natural fiber.</h1>
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
    <p class="dek"><a href="https://puroge.com/story/">{esc(SITE['dedication'])}</a></p>
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
