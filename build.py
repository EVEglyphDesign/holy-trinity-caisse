#!/usr/bin/env python3
"""
Build a static site from the packet markdown files.
Renders each doc into an HTML page under dist/, plus an index page.
"""
import os
import re
import shutil
from pathlib import Path

try:
    import markdown
except ImportError:
    import subprocess
    subprocess.check_call(["pip", "install", "--quiet", "markdown"])
    import markdown

ROOT = Path(__file__).parent
DOCS = ROOT / "docs"
DIST = ROOT / "dist"

# Order matters — this is the packet's read order
PAGES = [
    ("index.html", None, "The Holy Trinity Caisse", "index"),
    ("charter.html", "01_charter/charter.md", "Charter", "doc"),
    ("history.html", "02_history/desjardins_mcgivney.md", "Two Fathers of Mutual Aid", "doc"),
    ("dashboard.html", "03_dashboard/dashboard_spec.md", "Public Ledger — Dashboard", "doc"),
    ("economic-model.html", "04_amazon_math/procurement_math.md", "The Economic Model", "doc"),
    ("ledger-spec.html", "05_ledger_spec/README.md", "Ledger & Shop Technical Spec", "doc"),
    ("knights-letter.html", "06_knights_letter/knights_letter.md", "Knights Letter", "doc"),
    ("certification-flow.html", "07_certification_flow/flow.md", "Certification & Enrollment Flow", "doc"),
    ("content-pipeline.html", "08_content_platform/pipeline.md", "PAIX Witness Content Pipeline", "doc"),
    ("packet.html", "PACKET.md", "Packet Cover Index", "doc"),
]

NAV = [
    ("index.html", "Home"),
    ("charter.html", "Charter"),
    ("history.html", "Two Fathers"),
    ("economic-model.html", "Economic Model"),
    ("knights-letter.html", "Knights Letter"),
    ("packet.html", "Full Packet"),
]

CSS = """
:root {
  --ink: #1c1a17;
  --ink-soft: #4a4642;
  --parchment: #faf7f0;
  --parchment-warm: #f2ede1;
  --rule: #d8cfbc;
  --accent: #7a2828;
  --accent-soft: #a45050;
  --gold: #a68b3a;
}

* { box-sizing: border-box; }

html {
  font-size: 17px;
  scroll-behavior: smooth;
}

body {
  margin: 0;
  background: var(--parchment);
  color: var(--ink);
  font-family: 'Cormorant Garamond', 'Iowan Old Style', 'Palatino Linotype', Georgia, serif;
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

header.site {
  border-bottom: 1px solid var(--rule);
  background: var(--parchment-warm);
  padding: 1.4rem 0 1rem;
}
.wrap {
  max-width: 780px;
  margin: 0 auto;
  padding: 0 1.5rem;
}
.brand {
  display: flex;
  align-items: baseline;
  gap: 0.9rem;
  justify-content: space-between;
  flex-wrap: wrap;
}
.brand-title {
  font-size: 1.35rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: var(--ink);
  text-decoration: none;
}
.brand-title span {
  color: var(--accent);
}
.brand-tag {
  font-size: 0.85rem;
  font-style: italic;
  color: var(--ink-soft);
  letter-spacing: 0.03em;
}
nav.site {
  border-bottom: 1px solid var(--rule);
  background: var(--parchment);
  font-size: 0.86rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
nav.site .wrap {
  display: flex;
  gap: 1.4rem;
  padding-top: 0.65rem;
  padding-bottom: 0.65rem;
  flex-wrap: wrap;
}
nav.site a {
  color: var(--ink-soft);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  padding-bottom: 2px;
}
nav.site a:hover, nav.site a.current {
  color: var(--accent);
  border-bottom-color: var(--accent);
}

main {
  padding: 3rem 0 5rem;
}

h1, h2, h3, h4 {
  font-family: 'Cormorant Garamond', Georgia, serif;
  color: var(--ink);
  line-height: 1.25;
  margin-top: 2.2em;
  margin-bottom: 0.6em;
  font-weight: 600;
}
h1 { font-size: 2.4rem; margin-top: 0.3em; letter-spacing: -0.005em; }
h2 { font-size: 1.6rem; border-bottom: 1px solid var(--rule); padding-bottom: 0.25em; }
h3 { font-size: 1.22rem; color: var(--accent); }
h4 { font-size: 1.05rem; letter-spacing: 0.02em; }

p, li { font-size: 1.05rem; }
p { margin: 1em 0; }
ul, ol { padding-left: 1.6rem; }
li { margin: 0.35em 0; }

blockquote {
  border-left: 3px solid var(--accent);
  margin: 1.5em 0;
  padding: 0.2em 1.2em;
  color: var(--ink-soft);
  font-style: italic;
  background: rgba(122, 40, 40, 0.03);
}

em {
  font-style: italic;
  color: var(--ink-soft);
}
strong { color: var(--ink); }

a {
  color: var(--accent);
  text-decoration: none;
  border-bottom: 1px solid rgba(122, 40, 40, 0.35);
}
a:hover { border-bottom-color: var(--accent); }

hr {
  border: none;
  border-top: 1px solid var(--rule);
  margin: 2.4em 0;
}

code {
  font-family: 'JetBrains Mono', 'SF Mono', 'Menlo', monospace;
  font-size: 0.88em;
  background: rgba(122, 40, 40, 0.06);
  padding: 0.1em 0.35em;
  border-radius: 3px;
  color: var(--accent);
}
pre {
  background: #f5efe1;
  border: 1px solid var(--rule);
  padding: 1rem 1.2rem;
  overflow-x: auto;
  border-radius: 4px;
  font-size: 0.85rem;
  line-height: 1.5;
}
pre code {
  background: none;
  padding: 0;
  color: var(--ink);
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5em 0;
  font-size: 0.96rem;
}
th, td {
  border-bottom: 1px solid var(--rule);
  text-align: left;
  padding: 0.55em 0.75em;
  vertical-align: top;
}
th {
  background: var(--parchment-warm);
  font-weight: 600;
  font-family: 'Cormorant Garamond', Georgia, serif;
  color: var(--ink);
  letter-spacing: 0.02em;
}
tbody tr:hover { background: rgba(122, 40, 40, 0.02); }

footer.site {
  border-top: 1px solid var(--rule);
  padding: 2rem 0 3rem;
  font-size: 0.9rem;
  color: var(--ink-soft);
  text-align: center;
  font-style: italic;
}
footer.site a { color: var(--ink-soft); border-bottom-color: rgba(74, 70, 66, 0.3); }

/* Home page */
.hero {
  padding: 3rem 0 2rem;
  text-align: center;
}
.hero .rule {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 1.55rem;
  font-style: italic;
  color: var(--accent);
  margin: 1.4rem 0 2.2rem;
  letter-spacing: 0.03em;
}
.hero h1 {
  font-size: 2.7rem;
  margin: 0 0 0.4rem;
}
.hero .sub {
  font-size: 1.05rem;
  color: var(--ink-soft);
  font-style: italic;
}

.lanes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.2rem;
  margin: 3rem 0;
}
.lane {
  border: 1px solid var(--rule);
  padding: 1.2rem 1.3rem 1.4rem;
  background: var(--parchment-warm);
  border-radius: 4px;
}
.lane .num {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 2.2rem;
  color: var(--accent);
  line-height: 1;
  margin-bottom: 0.3rem;
}
.lane h3 {
  margin: 0 0 0.4rem;
  font-size: 1.15rem;
  color: var(--ink);
}
.lane p {
  font-size: 0.95rem;
  margin: 0;
  color: var(--ink-soft);
}

.docs-list {
  margin: 2rem 0;
}
.docs-list a.doc-row {
  display: block;
  border-bottom: 1px solid var(--rule);
  padding: 1rem 0;
  color: var(--ink);
  border-bottom-color: var(--rule);
  transition: background 0.15s;
}
.docs-list a.doc-row:last-child { border-bottom: none; }
.docs-list a.doc-row:hover {
  background: rgba(122, 40, 40, 0.03);
  padding-left: 0.5rem;
}
.docs-list .doc-title {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 1.25rem;
  font-weight: 600;
  display: block;
  color: var(--ink);
}
.docs-list .doc-desc {
  font-size: 0.9rem;
  color: var(--ink-soft);
  font-style: italic;
  margin-top: 0.15rem;
}

.callout {
  border: 1px solid var(--rule);
  background: var(--parchment-warm);
  padding: 1.3rem 1.6rem;
  margin: 2rem 0;
  border-radius: 4px;
}
.callout h3 { margin-top: 0; }

@media (max-width: 640px) {
  html { font-size: 16px; }
  .hero h1 { font-size: 2rem; }
  h1 { font-size: 1.9rem; }
  h2 { font-size: 1.4rem; }
}
"""

BASE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Holy Trinity Caisse</title>
<meta name="description" content="The Holy Trinity Caisse — a parish-scale mutual-aid economy under the umbrella of PAIX.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%23faf7f0'/%3E%3Ctext x='16' y='23' text-anchor='middle' font-family='Georgia' font-size='22' fill='%237a2828' font-weight='600'%3E%E2%9C%9D%3C/text%3E%3C/svg%3E">
</head>
<body>
<header class="site">
  <div class="wrap">
    <div class="brand">
      <a href="index.html" class="brand-title">Holy Trinity <span>Caisse</span></a>
      <span class="brand-tag">A parish mutual-aid economy · under PAIX</span>
    </div>
  </div>
</header>
<nav class="site">
  <div class="wrap">
    {nav}
  </div>
</nav>
<main>
  <div class="wrap">
    {body}
  </div>
</main>
<footer class="site">
  <div class="wrap">
    <p><em>The Fathers' work, continued. Vivat Jesus.</em></p>
    <p>One good deed. One witness. One hour. One token.</p>
  </div>
</footer>
</body>
</html>
"""


def nav_html(current):
    parts = []
    for href, label in NAV:
        cls = ' class="current"' if href == current else ''
        parts.append(f'<a href="{href}"{cls}>{label}</a>')
    return "\n    ".join(parts)


def render_markdown(md_text):
    # Convert markdown to HTML with tables + fenced code + attr_list
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "attr_list", "toc"],
        extension_configs={"toc": {"permalink": False}},
    )
    html = md.convert(md_text)
    # Rewrite relative markdown links to our html routes
    link_map = {}
    for out_name, src_rel, _title, _kind in PAGES:
        if src_rel:
            link_map[src_rel] = out_name
            link_map[src_rel.replace("/", "\\/")] = out_name
    for src_rel, target in link_map.items():
        html = html.replace(f'href="{src_rel}"', f'href="{target}"')
        # Also handle prefixed patterns
        html = html.replace(f'href="../{src_rel}"', f'href="{target}"')
    return html


def build_index():
    body = """
<section class="hero">
  <h1>The Holy Trinity Caisse</h1>
  <p class="sub">A parish-scale mutual-aid economy. Under the umbrella of PAIX.<br>
     The Fathers' work, continued — with the technology of our own century.</p>
  <div class="rule">One good deed. One witness. One hour. One token.</div>
</section>

<section>
  <h2>Four lanes. One caisse. One neighbor served.</h2>
  <div class="lanes">
    <div class="lane">
      <div class="num">I</div>
      <h3>Certified shopping</h3>
      <p>Any parishioner in good standing is certified by the parish and their ordinary purchases quietly direct the stewardship spread — about 17% — into the common fund.</p>
    </div>
    <div class="lane">
      <div class="num">II</div>
      <h3>Deeds &amp; donations</h3>
      <p>An hour of service witnessed and signed into the ledger becomes one token. Dollar donors, moved by the works being done, feed the same fund.</p>
    </div>
    <div class="lane">
      <div class="num">III</div>
      <h3>PAIX Witness</h3>
      <p>Deed clips published under a shared Catholic imprint on YouTube, X, and Meta. All monetization returns to the caisse. Attention becomes bread.</p>
    </div>
    <div class="lane">
      <div class="num">IV</div>
      <h3>Professional services</h3>
      <p>An hour of a professional's trade, donated to a neighbor at full market rate. The provider chooses 0–30% walk-away as caisse credit for their own household.</p>
    </div>
  </div>
</section>

<section class="callout">
  <h3>The whole ambition</h3>
  <p><strong>We do not invent. We continue.</strong> Alphonse Desjardins captured a Catholic people's savings flow and redirected it to their own; Father McGivney captured the same people's insurance flow and did likewise. The Holy Trinity Caisse turns the same wheel a third time.</p>
  <p>Same instinct. Four flows. One caisse. One neighbor served.</p>
</section>

<section>
  <h2>The founding packet</h2>
  <div class="docs-list">
    <a class="doc-row" href="charter.html">
      <span class="doc-title">I. The Charter</span>
      <span class="doc-desc">The Rule, six Articles, five Flows, the Order, the Fathers' Work Continued, the Posture, the Promise, the Public Witness</span>
    </a>
    <a class="doc-row" href="history.html">
      <span class="doc-title">II. Two Fathers of Mutual Aid</span>
      <span class="doc-desc">Desjardins and McGivney — one page placing the caisse as the third turn of the same wheel</span>
    </a>
    <a class="doc-row" href="dashboard.html">
      <span class="doc-title">III. The Public Ledger — Dashboard Specification</span>
      <span class="doc-desc">Nine metrics, refreshed nightly, at a permanent public URL</span>
    </a>
    <a class="doc-row" href="economic-model.html">
      <span class="doc-title">IV. The Economic Model</span>
      <span class="doc-desc">Four-lane math, year-1/2/3 realistic ramp, sourced line by line</span>
    </a>
    <a class="doc-row" href="ledger-spec.html">
      <span class="doc-title">V. Ledger, Shop &amp; PAIX Witness Technical Spec</span>
      <span class="doc-desc">Nine tables, SQLite spine, vendor and platform abstractions, buildable in one week</span>
    </a>
    <a class="doc-row" href="knights-letter.html">
      <span class="doc-title">VI. Knights Letter</span>
      <span class="doc-desc">The invitation to the first Grand Knight, with three honest caveats named plainly</span>
    </a>
    <a class="doc-row" href="certification-flow.html">
      <span class="doc-title">VII. Certification &amp; Enrollment Flow</span>
      <span class="doc-desc">30-second parishioner UX, 3-minute steward nightly queue, professional-services enrollment sub-flow</span>
    </a>
    <a class="doc-row" href="content-pipeline.html">
      <span class="doc-title">VIII. PAIX Witness Content Pipeline</span>
      <span class="doc-desc">Capture through revenue reporting, with the guardrails encoded rather than proclaimed</span>
    </a>
    <a class="doc-row" href="packet.html">
      <span class="doc-title">Cover Index — the full packet in one page</span>
      <span class="doc-desc">Everything above, in reading order, with the three honest caveats and the whole ambition</span>
    </a>
  </div>
</section>

<section class="callout">
  <h3>What this packet asks</h3>
  <p>Not money. Not endorsement of a concept. Not a program integration.</p>
  <ul>
    <li><strong>From the pastor:</strong> a blessing, and permission to be kept under the parish's roof.</li>
    <li><strong>From the Knights:</strong> recognition as consistent with Father McGivney's charism, and a nominated council of witnesses.</li>
    <li><strong>From diocesan counsel:</strong> a blessing of the walk-away structure and IRS receipt language for the professional-services lane, before the first professional is enrolled.</li>
    <li><strong>From the parishioners:</strong> nothing yet. The caisse is offered, not imposed.</li>
  </ul>
</section>
"""
    return body


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    # Write CSS
    (DIST / "style.css").write_text(CSS)

    # Render each page
    for out_name, src_rel, title, kind in PAGES:
        if kind == "index":
            body = build_index()
        else:
            src = DOCS / src_rel
            md_text = src.read_text()
            body = render_markdown(md_text)

        html = BASE_TEMPLATE.format(
            title=title,
            nav=nav_html(out_name),
            body=body,
        )
        (DIST / out_name).write_text(html)
        print(f"  built {out_name}")

    print(f"Site built at {DIST}")


if __name__ == "__main__":
    main()
