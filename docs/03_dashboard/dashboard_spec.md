# Holy Trinity Caisse — Public Dashboard Specification

*"For a caisse that hides its ledger has already ceased to be one."* — Charter, §The Promise

## Purpose

A single public page — no login, no analytics, no ads — that renders the numbers a skeptic can use to verify the caisse is real, solvent, and doing what it claims. Refreshed nightly from the ledger. Anyone can bookmark it and check.

**URL (proposed):** `caisse.holytrinity.example.org/ledger` (or `holytrinitycaisse.example.org` for a standalone shell)

## The Seven Proof-Metrics

Each metric has a headline number, a plain-English definition, a target band, and a sparkline of the last 12 weeks.

### 1. Token Velocity

> **Median days from token earned to token spent.**

- **Proves:** Deeds are being done and redeemed. Tokens are not hoarded (theatre) or dying in dormant accounts (shop doesn't stock what people need).
- **Target band:** 30–90 days.
- **Alert if:** > 180 days (catalog problem) or < 7 days (possible round-tripping — investigate).
- **Displayed as:** *"Median token lifespan: **47 days.** Half of tokens earned are spent within 47 days of the deed."*

### 2. Fund Solvency Ratio

> **Dollars in the pooled fund ÷ outstanding token liability.**

- **Proves:** The caisse can settle every token in circulation with a vendor payment. Below 1.0, the caisse is technically insolvent.
- **Target band:** ≥ $1.00 per outstanding token.
- **Alert if:** < $0.75 (call the stewards) or > $3.00 (donors outpacing deed-earners — expand catalog or witness network).
- **Displayed as:** *"Solvency: **$1.24 per token.** For every token in a parishioner's account, the fund holds $1.24 to settle it."*

### 3. Procurement Spread

> **(Retail dollar value delivered − Actual dollars paid to vendors) ÷ Retail dollar value delivered.**

- **Proves:** The Amazon Business + ATEP + OMNIA + rebate stack is delivering the claimed savings. This is the parish's version of a caisse populaire's interest spread.
- **Target band:** ≥ 15%.
- **Alert if:** < 10% (renegotiate with account executive) or > 30% (verify math — likely category-mix issue).
- **Displayed as:** *"Spread: **17.3%.** For every $100 of goods delivered at retail value, the caisse pays $82.70 — the difference is stewardship, not profit."*

### 4. Deed Diversity Index

> **Count of distinct earner-parishioners in the trailing 90 days.**

- **Proves:** The caisse is a network, not a household. Diversity is what makes it *catholic* (small-c: universal).
- **Target band:** ≥ 20 in the first 6 months; ≥ 50 by end of year 1.
- **Alert if:** < 10 for two consecutive months (witness network too small).
- **Displayed as:** *"Contributors: **34 parishioners.** Distinct people who earned at least one token in the last 90 days."*

### 5. Household Participation Rate

> **% of parish households that routed at least one certified purchase through the caisse in the trailing 90 days.**

- **Proves:** The parish has actually shifted its consumer behavior. This is the metric that says lane 1 (certified shopping) is real, not aspirational.
- **Target band:** ≥ 40% by end of year 1; ≥ 60% by end of year 2.
- **Alert if:** < 20% at end of quarter 2 (the certification funnel is broken; steward outreach needed).
- **Displayed as:** *"Participation: **43% of households.** 187 of 434 registered households shopped through the caisse in the last 90 days."*

### 6. Deed Video Coverage

> **% of deeds in the ledger that carry a linked video record (unlisted or public) on at least one witness platform.**

- **Proves:** The caisse doesn't just count deeds; it can show them. This is the honesty metric — the check against a ledger inflated by paper attestations.
- **Target band:** ≥ 85% by end of year 1.
- **Alert if:** < 60% (evidence workflow is failing; retrain witnesses).
- **Displayed as:** *"Video-witnessed: **91% of deeds.** 374 of the 412 deeds this quarter carry a video record."*

### 7. Public Witness Revenue

> **Dollars flowing to the caisse fund from public witness platforms in the trailing quarter, itemized by platform.**

- **Proves:** Lane 3 is real. The parish's public witness is not merely propagation; it is a self-funding surface.
- **Target band:** Any positive figure in year 1; ≥ $10,000/year by end of year 2 (single-platform threshold).
- **Alert if:** No revenue for three consecutive quarters after channels reach eligibility (propagation cadence is broken).
- **Displayed as:** *"Public witness revenue this quarter: **$1,687**"* — with per-platform breakdown table:

  | Platform | Revenue Q3 2026 | Status |
  |---|---|---|
  | YouTube | $847 | Monetized |
  | X | $312 | Monetized |
  | Meta (IG/FB) | $528 | Monetized |
  | Other | $0 | — |

## The Page, Written Out

```
────────────────────────────────────────────────
  HOLY TRINITY CAISSE — Public Ledger
  Updated nightly · Last refresh: 2026-07-18 23:00 CDT
────────────────────────────────────────────────

  Token lifespan          Solvency
  47 days                 $1.24 per token
  ▁▂▃▃▄▅▄▅▆▅▆▇            ▄▅▅▆▆▇▇▇▆▇▇▇

  Procurement spread      Contributors (90d)
  17.3%                   34 parishioners
  ▂▃▄▄▅▆▆▇▇▇▇▇            ▁▂▂▃▃▄▄▅▅▆▆▇

  Household participation Video coverage
  43% of households       91% of deeds
  ▂▃▃▄▄▅▅▆▆▆▇▇            ▄▅▅▆▆▇▇▇▇▇▇▇

  Public witness revenue (this quarter)
  $1,687   [YouTube $847 · X $312 · Meta $528]

────────────────────────────────────────────────
  Tokens earned this quarter:     412
  Tokens spent this quarter:      378
  Certified households:           434
  Certified purchases (Q):        1,247 · $18,340 retail
  Spread returned to fund (Q):    $3,162
  Dollars donated (Q):            $9,840
  Public witness revenue (Q):     $1,687
  ─────────────────────────────
  Total fund inflow (Q):          $14,689
  Dollars paid to vendors:        $12,203
  Retail value delivered:         $19,285
────────────────────────────────────────────────

  Full charter · Quarterly report (PDF) · About PAIX
────────────────────────────────────────────────
```

That is the whole page. No dashboards behind logins. No aggregate charts of individual behavior. Parishioner names are never on this page — only counts.

## The Public Deed Wall

A separate page at `caisse.holytrinity.example.org/deeds` renders the wall of publicly-consented deed clips as a grid of thumbnails, each 20–90 seconds, each with:

- Deed category (elder transport, tutoring, meal delivery, etc.)
- Month and year
- The witness's name (never the beneficiary's, unless they explicitly opted in)
- A click-through to the clip on its home platform (YouTube for the durable archive; X and Meta as propagation surfaces linked from the same source)

Only deeds with `youtube_privacy = 'public'` AND `beneficiary_consent_given = 1` appear on this wall. Unlisted deeds still count in ledger aggregates but do not appear.

The wall is the evangelism surface — the place a Grand Knight sends his brothers on Monday morning, the place a bishop's communications office finds material, the place a mother in Missouri sees her son's Knights of Columbus witness clip.

## Data Sources

- **Ledger DB** (SQLite, `holy-trinity-caisse` repo) — deeds, witnesses, redemptions, transfers, certifications.
- **Vendor invoice log** (Amazon Business exports + local merchant receipts) — actual dollars paid.
- **Donor CRM** (Stripe + manual entries) — dollars in.
- **Catalog** (`shop.config.json`) — retail prices, token prices, actual expected prices.
- **Platform revenue exports** (YouTube AdSense CSV, X Creator monetization report, Meta Creator Studio) — imported monthly into `revenue/YYYY-MM.json`.

A nightly Node script recomputes all seven metrics and writes them to `public/ledger.json`, which the static page reads.

## What is *not* on the dashboard

Deliberately absent:

- **Individual parishioner balances or names.** Ever. The witness ledger is stewarded, not published.
- **Beneficiary faces in aggregate imagery.** The Public Deed Wall shows only doer-and-witness clips or auto-blurred beneficiary clips.
- **Donor amounts by name.** Aggregate only, unless the donor explicitly consents to be listed.
- **Growth vanity metrics.** No "signups," no "engagement," no MAU. The caisse is not a platform.
- **Charity-porn imagery.** No "meet the family we helped." Dignity is structural, not decorative.

## What this dashboard enables

When a Grand Knight, a bishop, an auditor, or a skeptical journalist visits `caisse.holytrinity.example.org/ledger`, they can — in under thirty seconds — determine:

1. Is anything actually happening? *(Token velocity, contributors, participation.)*
2. Is it solvent? *(Fund solvency ratio.)*
3. Is the economic thesis real? *(Procurement spread, spread returned to fund.)*
4. Is it a real network, or a two-family favor economy? *(Deed diversity, participation rate.)*
5. Can the deeds be seen, or only claimed? *(Video coverage.)*
6. Does the public witness pay for itself? *(PAIX Witness revenue.)*
7. Is the parish's professional class contributing, and at what personal cost? *(Professional services delivered + average walk-away.)*

If those nine numbers hold for two quarters, PAIX has proven its economic model. That is the entire point.
