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
    ("world-fund.html", "09_world_fund/world_fund.md", "PAIX World Fund", "doc"),
    ("packet.html", "PACKET.md", "Packet Cover Index", "doc"),
]

NAV = [
    ("index.html", "Home"),
    ("charter.html", "Charter"),
    ("history.html", "Two Fathers"),
    ("economic-model.html", "Economic Model"),
    ("knights-letter.html", "Knights Letter"),
    ("world-fund.html", "World Fund"),
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
  font-size: 16px;
  scroll-behavior: smooth;
  overflow-x: hidden;
}

body {
  margin: 0;
  background: var(--parchment);
  color: var(--ink);
  font-family: 'Source Serif 4', 'Charter', 'Iowan Old Style', Georgia, serif;
  font-weight: 450;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
  overflow-x: hidden;
}

header.site {
  border-bottom: 1px solid var(--rule);
  background: var(--parchment-warm);
  padding: 0.9rem 0 0.75rem;
}
.wrap {
  max-width: 820px;
  margin: 0 auto;
  padding: 0 1.1rem;
}
.brand {
  display: flex;
  align-items: baseline;
  gap: 0.9rem;
  justify-content: space-between;
  flex-wrap: wrap;
}
.brand-title {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--ink);
  text-decoration: none;
}
.brand-title span {
  color: var(--accent);
}
.brand-tag {
  font-family: 'Inter', -apple-system, sans-serif;
  font-size: 0.78rem;
  font-weight: 400;
  color: var(--ink-soft);
  letter-spacing: 0.01em;
}
.pre-approval {
  background: #fdf5df;
  border-top: 1px solid #d8c992;
  border-bottom: 1px solid #d8c992;
  color: #5a4a10;
  padding: 0.5rem 0;
  font-size: 0.82rem;
  line-height: 1.4;
  font-family: 'Inter', -apple-system, sans-serif;
  font-weight: 450;
  text-align: left;
}
.pre-approval strong { color: #3a3008; letter-spacing: 0.05em; text-transform: uppercase; font-size: 0.7rem; font-weight: 700; }
.pre-approval .wrap { max-width: 820px; padding: 0 1.1rem; margin: 0 auto; }
nav.site {
  border-bottom: 1px solid var(--rule);
  background: var(--parchment);
  font-family: 'Inter', -apple-system, sans-serif;
  font-size: 0.78rem;
  font-weight: 500;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
nav.site .wrap {
  display: flex;
  gap: 1.1rem;
  padding-top: 0.55rem;
  padding-bottom: 0.55rem;
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
  padding: 1.6rem 0 3rem;
}

h1, h2, h3, h4 {
  font-family: 'Source Serif 4', Charter, Georgia, serif;
  color: var(--ink);
  line-height: 1.2;
  margin-top: 1.6em;
  margin-bottom: 0.4em;
  font-weight: 700;
  letter-spacing: -0.015em;
}
h1 { font-size: 1.85rem; margin-top: 0.2em; }
h2 { font-size: 1.35rem; border-bottom: 1px solid var(--rule); padding-bottom: 0.2em; margin-top: 1.8em; }
h3 { font-size: 1.1rem; color: var(--accent); margin-top: 1.4em; }
h4 { font-size: 1rem; letter-spacing: 0; }

p, li { font-size: 1rem; }
p { margin: 0.75em 0; }
ul, ol { padding-left: 1.4rem; margin: 0.6em 0; }
li { margin: 0.2em 0; }

blockquote {
  border-left: 3px solid var(--accent);
  margin: 1em 0;
  padding: 0.4em 1em;
  color: var(--ink);
  background: rgba(122, 40, 40, 0.04);
  font-size: 0.98rem;
}
blockquote p { margin: 0.4em 0; }

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

.table-wrap { overflow-x: auto; margin: 1em -0.5rem; padding: 0 0.5rem; }
table {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
  font-size: 0.9rem;
  font-family: 'Inter', -apple-system, sans-serif;
}
th, td {
  border-bottom: 1px solid var(--rule);
  text-align: left;
  padding: 0.5em 0.6em;
  vertical-align: top;
  line-height: 1.4;
}
th {
  background: var(--parchment-warm);
  font-weight: 600;
  color: var(--ink);
  letter-spacing: 0;
  font-size: 0.85rem;
  text-transform: uppercase;
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
  padding: 1.2rem 0 1.4rem;
  text-align: left;
  border-bottom: 1px solid var(--rule);
  margin-bottom: 1.8rem;
}
.hero .rule {
  font-family: 'Source Serif 4', Charter, Georgia, serif;
  font-size: 1.15rem;
  font-weight: 600;
  font-style: italic;
  color: var(--accent);
  margin: 0.9rem 0 0.4rem;
  letter-spacing: 0;
}
.hero h1 {
  font-size: 2rem;
  margin: 0 0 0.3rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}
.hero .sub {
  font-size: 1rem;
  color: var(--ink-soft);
  font-style: normal;
  margin: 0;
  line-height: 1.5;
}

.lanes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.8rem;
  margin: 1.5rem 0 2rem;
}
.lane {
  border: 1px solid var(--rule);
  padding: 0.8rem 0.95rem 0.95rem;
  background: var(--parchment-warm);
  border-radius: 3px;
}
.lane .num {
  font-family: 'Source Serif 4', Charter, Georgia, serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent);
  line-height: 1;
  margin-bottom: 0.2rem;
}
.lane h3 {
  margin: 0 0 0.25rem;
  font-size: 1rem;
  color: var(--ink);
  font-weight: 600;
}
.lane p {
  font-size: 0.9rem;
  margin: 0;
  color: var(--ink);
  line-height: 1.45;
}

.docs-list {
  margin: 2rem 0;
}
.docs-list a.doc-row {
  display: block;
  border-bottom: 1px solid var(--rule);
  padding: 0.65rem 0;
  color: var(--ink);
  transition: background 0.15s;
}
.docs-list a.doc-row:last-child { border-bottom: none; }
.docs-list a.doc-row:hover {
  background: rgba(122, 40, 40, 0.04);
  padding-left: 0.4rem;
}
.docs-list .doc-title {
  font-family: 'Source Serif 4', Charter, Georgia, serif;
  font-size: 1.05rem;
  font-weight: 600;
  display: block;
  color: var(--ink);
}
.docs-list .doc-desc {
  font-size: 0.88rem;
  color: var(--ink-soft);
  font-style: normal;
  margin-top: 0.1rem;
  line-height: 1.4;
}

.callout {
  border: 1px solid var(--rule);
  background: var(--parchment-warm);
  padding: 0.9rem 1.1rem;
  margin: 1.4rem 0;
  border-radius: 3px;
}
.callout h3 { margin-top: 0; }
.callout p:last-child { margin-bottom: 0; }

@media (max-width: 640px) {
  html { font-size: 15.5px; }
  .wrap { padding: 0 0.9rem; }
  .hero { padding: 1rem 0 1.1rem; }
  .hero h1 { font-size: 1.65rem; }
  h1 { font-size: 1.55rem; }
  h2 { font-size: 1.2rem; }
  h3 { font-size: 1.02rem; }
  main { padding: 1.2rem 0 2.4rem; }
  table { font-size: 0.82rem; }
  th, td { padding: 0.35em 0.45em; }
  .brand { flex-direction: column; align-items: flex-start; gap: 0.15rem; }
  .brand-title { font-size: 1rem; }
  .brand-tag { font-size: 0.72rem; }
  nav.site { font-size: 0.72rem; }
  nav.site .wrap { gap: 0.75rem 1rem; }
  .pre-approval { font-size: 0.76rem; }
  .pre-approval strong { font-size: 0.65rem; }
  .lanes { grid-template-columns: 1fr; gap: 0.7rem; margin: 1.2rem 0 1.6rem; }
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
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600;8..60,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
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
<div class="pre-approval">
  <div class="wrap">
    <strong>Pre-approval</strong> · This is a proposal being prepared for Holy Trinity Parish, Lenexa. Nothing here has been blessed by a pastor, approved by a chancery, or negotiated with Amazon.
  </div>
</div>
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
    # Also rewrite any absolute /docs/... links to relative html routes
    html = re.sub(r'href="/docs/([^"]+)"', r'href="\1"', html)
    # Wrap each <table> in a scroll container so mobile can pan wide tables
    html = re.sub(r'<table>', r'<div class="table-wrap"><table>', html)
    html = re.sub(r'</table>', r'</table></div>', html)
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
