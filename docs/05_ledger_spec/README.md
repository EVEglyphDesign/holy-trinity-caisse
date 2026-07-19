# Holy Trinity Caisse — Ledger, Shop & PAIX Witness Technical Spec

This is the technical spine of the caisse. It is intentionally small. The whole thing should fit in one repository, one steward's head, and one page of documentation. It covers **four lanes**: certified shopping, deeds & donations, PAIX Witness content, and professional services.

## Repository structure

Fork the existing storage shop into a new repo:

```
holy-trinity-caisse/
├── README.md                       # This file
├── charter.md                      # Framed copy of the charter
├── shop.config.json                # Catalog, certification policy, video policy, prof-services policy
├── data/
│   ├── caisse.db                   # SQLite ledger (all four lanes)
│   ├── donors.csv                  # Stripe-synced donor log
│   └── vendor_receipts/            # Invoices from Amazon Business + local merchants
├── revenue/                        # Monthly platform revenue imports (lane 3)
│   ├── youtube_YYYY-MM.json
│   ├── x_YYYY-MM.json
│   └── meta_YYYY-MM.json
├── public/
│   ├── index.html                  # Public shop skin
│   ├── ledger.html                 # Nine-metric dashboard
│   ├── deeds.html                  # Public Deed Wall (curated public clips)
│   └── ledger.json                 # Nightly-computed metrics
├── steward/                        # Steward-only (auth-gated) pages
│   ├── queue.html                  # Certification + deed + prof-services review
│   ├── attest.html                 # Witness signs a deed
│   ├── approve.html                # Steward approves a redemption
│   ├── order.html                  # Steward places the vendor order
│   ├── prof_service.html           # Log a professional service, set walk-away
│   └── publish.html                # Approve/reject video for public wall + cross-post
├── vendors/
│   ├── amazon.js                   # Amazon Business order interface
│   ├── local_grocer.js             # Template for signed-covenant local merchants
│   └── manual.js                   # Fallback: paste tracking number
├── platforms/                      # PAIX Witness cross-post interfaces
│   ├── youtube.js                  # YouTube Data API (upload, playlist, unlisted/public)
│   ├── x.js                        # X (Twitter) API (post video, attribution link)
│   └── meta.js                     # Meta Graph API (IG Reels, FB Reels)
├── scripts/
│   ├── mint_token.js               # Called by witness after attesting a deed
│   ├── mint_credit.js              # Called after professional-service attestation
│   ├── redeem.js                   # Debits tokens/credit, queues steward approval
│   ├── settle.js                   # Debits fund, records vendor payment
│   ├── cross_post.js               # Push clip to YouTube + X + Meta
│   ├── import_revenue.js           # Monthly platform revenue CSV → revenue/*.json
│   └── recompute_metrics.js        # Nightly cron
└── .github/workflows/
    ├── nightly.yml                 # Recompute metrics 23:00 CT
    └── monthly_revenue.yml         # First of month: import platform revenue
```

## The database: `caisse.db` (SQLite)

Nine tables. That is the whole ledger.

### 1. Parishioners (the certification roll)

```sql
CREATE TABLE parishioners (
  id INTEGER PRIMARY KEY,
  phone TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL,
  claimed_parish TEXT,
  code TEXT UNIQUE,                        -- 'HT-4291-KANE'; null until certified
  household_id INTEGER,
  status TEXT NOT NULL DEFAULT 'pending',  -- pending | certified | flagged | declined
  certified_on DATETIME,
  certified_by INTEGER REFERENCES parishioners(id),
  auto_approved BOOLEAN DEFAULT 0,
  notes TEXT,
  joined_on DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE VIEW v_certification_queue AS
  SELECT id, phone, display_name, claimed_parish, joined_on
  FROM parishioners
  WHERE status = 'pending'
  ORDER BY joined_on ASC;
```

### 2. Deeds (lane 2: the token lane)

```sql
CREATE TABLE deeds (
  id INTEGER PRIMARY KEY,
  earner_id INTEGER NOT NULL REFERENCES parishioners(id),
  witness_id INTEGER NOT NULL REFERENCES parishioners(id),
  description TEXT NOT NULL,
  hours REAL NOT NULL,
  performed_on DATE NOT NULL,
  attested_on DATETIME NOT NULL,
  video_id INTEGER REFERENCES videos(id),
  CHECK (earner_id != witness_id)
);
```

### 3. Professional services (lane 4: the credit lane)

```sql
CREATE TABLE parishioner_credentials (
  id INTEGER PRIMARY KEY,
  parishioner_id INTEGER NOT NULL REFERENCES parishioners(id),
  credential_type TEXT NOT NULL,           -- 'jd_bar', 'md', 'cpa', 'plumbing_license', ...
  credential_ref TEXT,
  jurisdiction TEXT,
  standard_market_rate_dollars_per_hour REAL NOT NULL,
  default_walkaway_fraction REAL NOT NULL DEFAULT 0.20,
  verified_on DATE,
  verified_by INTEGER REFERENCES parishioners(id),
  CHECK (default_walkaway_fraction >= 0.0 AND default_walkaway_fraction <= 0.30)
);

CREATE TABLE professional_services (
  id INTEGER PRIMARY KEY,
  provider_id INTEGER NOT NULL REFERENCES parishioners(id),
  service_category TEXT NOT NULL,
  service_description TEXT NOT NULL,
  recipient_id INTEGER REFERENCES parishioners(id),      -- null = parish itself
  recipient_witness_id INTEGER REFERENCES parishioners(id),
  market_rate_dollars_per_hour REAL NOT NULL,
  hours REAL NOT NULL,
  market_value_dollars REAL NOT NULL,                    -- hours × rate
  walkaway_fraction REAL NOT NULL,                       -- 0.00 to 0.30
  credit_dollars_to_provider REAL NOT NULL,              -- market_value × walkaway
  net_value_to_caisse REAL NOT NULL,                     -- market_value - credit
  performed_on DATE NOT NULL,
  attested_on DATETIME NOT NULL,
  irs_receipt_issued BOOLEAN DEFAULT 0,
  video_id INTEGER REFERENCES videos(id),
  CHECK (walkaway_fraction >= 0.0 AND walkaway_fraction <= 0.30),
  CHECK (provider_id != recipient_id OR recipient_id IS NULL)
);
```

### 4. Donations (lane 2: the dollar-donor side)

```sql
CREATE TABLE donations (
  id INTEGER PRIMARY KEY,
  donor_ref TEXT,
  amount_dollars REAL NOT NULL,
  sponsored_parishioner_id INTEGER,
  received_on DATE NOT NULL,
  receipt_issued BOOLEAN DEFAULT 0
);
```

### 5. Certified purchases (lane 1)

```sql
CREATE TABLE certified_purchases (
  id INTEGER PRIMARY KEY,
  parishioner_id INTEGER NOT NULL REFERENCES parishioners(id),
  item_id TEXT NOT NULL,
  retail_paid_dollars REAL NOT NULL,       -- what the parishioner paid
  actual_cost_dollars REAL,                -- what the caisse paid the vendor
  spread_to_fund REAL,                     -- retail - actual
  vendor_order_ref TEXT,
  ordered_on DATETIME NOT NULL,
  fulfilled_on DATETIME
);
```

### 6. Redemptions (spend lane: tokens or credit or mixed)

```sql
CREATE TABLE redemptions (
  id INTEGER PRIMARY KEY,
  parishioner_id INTEGER NOT NULL REFERENCES parishioners(id),
  item_id TEXT NOT NULL,
  tokens_spent REAL NOT NULL DEFAULT 0,
  credit_dollars_spent REAL NOT NULL DEFAULT 0,
  dollars_spent REAL NOT NULL DEFAULT 0,
  requested_on DATETIME NOT NULL,
  approved_on DATETIME,
  approved_by INTEGER REFERENCES parishioners(id),
  vendor_order_ref TEXT,
  vendor_dollars_paid REAL,
  fulfilled_on DATETIME
);
```

### 7. Transfers (token or credit gifts within family or back to parish)

```sql
CREATE TABLE transfers (
  id INTEGER PRIMARY KEY,
  from_parishioner_id INTEGER NOT NULL REFERENCES parishioners(id),
  to_parishioner_id INTEGER,               -- null = returned to parish pool
  tokens REAL DEFAULT 0,
  credit_dollars REAL DEFAULT 0,
  reason TEXT,
  transferred_on DATETIME NOT NULL
);
```

### 8. Videos (lane 3: the PAIX Witness capture layer)

```sql
CREATE TABLE videos (
  id INTEGER PRIMARY KEY,
  raw_upload_id TEXT,                      -- local file ref or storage URL
  youtube_video_id TEXT,
  x_post_id TEXT,
  meta_ig_reel_id TEXT,
  meta_fb_reel_id TEXT,
  privacy TEXT NOT NULL DEFAULT 'unlisted',-- unlisted | public
  doer_face_visible BOOLEAN DEFAULT 1,
  beneficiary_face_visible BOOLEAN DEFAULT 0,
  beneficiary_consent_given BOOLEAN DEFAULT 0,
  monetization_consent_given BOOLEAN DEFAULT 0,
  minor_present BOOLEAN DEFAULT 0,
  guardian_consent_given BOOLEAN DEFAULT 0,
  auto_review_passed BOOLEAN,
  steward_review_status TEXT DEFAULT 'pending', -- pending | approved | rejected
  steward_review_by INTEGER REFERENCES parishioners(id),
  captured_on DATETIME NOT NULL,
  published_on DATETIME
);
```

### 9. Platform revenue (lane 3: the money side)

```sql
CREATE TABLE platform_revenue (
  id INTEGER PRIMARY KEY,
  platform TEXT NOT NULL,                  -- 'youtube' | 'x' | 'meta_ig' | 'meta_fb' | 'other'
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  gross_revenue_dollars REAL NOT NULL,
  platform_fee_dollars REAL DEFAULT 0,
  net_to_caisse_dollars REAL NOT NULL,
  import_source TEXT,                      -- 'youtube_adsense_csv', 'x_creator_report', etc.
  imported_on DATETIME NOT NULL
);
```

## Views for the dashboard

```sql
-- Token velocity (median days earned → spent)
CREATE VIEW v_token_velocity AS
  SELECT r.parishioner_id,
         julianday(r.approved_on) - julianday(d.attested_on) AS days_to_spend
  FROM redemptions r JOIN deeds d ON d.earner_id = r.parishioner_id
  WHERE r.approved_on IS NOT NULL AND r.tokens_spent > 0;

-- Fund solvency (four-lane accounting)
CREATE VIEW v_solvency AS
  SELECT
    (SELECT COALESCE(SUM(amount_dollars),0) FROM donations)
    + (SELECT COALESCE(SUM(spread_to_fund),0) FROM certified_purchases)
    + (SELECT COALESCE(SUM(net_to_caisse_dollars),0) FROM platform_revenue)
    - (SELECT COALESCE(SUM(vendor_dollars_paid),0) FROM redemptions)
    AS fund_dollars,
    (SELECT COALESCE(SUM(hours),0) FROM deeds)
    - (SELECT COALESCE(SUM(tokens_spent),0) FROM redemptions)
    AS outstanding_tokens,
    (SELECT COALESCE(SUM(credit_dollars_to_provider),0) FROM professional_services)
    - (SELECT COALESCE(SUM(credit_dollars_spent),0) FROM redemptions)
    AS outstanding_credit_dollars;

-- Procurement spread (lane 1)
CREATE VIEW v_spread AS
  SELECT SUM(retail_paid_dollars) AS retail_delivered,
         SUM(actual_cost_dollars) AS actual_paid,
         SUM(spread_to_fund) AS spread_captured
  FROM certified_purchases
  WHERE fulfilled_on IS NOT NULL;

-- Deed diversity (trailing 90 days)
CREATE VIEW v_diversity AS
  SELECT COUNT(DISTINCT earner_id) AS distinct_earners
  FROM deeds WHERE performed_on >= date('now','-90 days');

-- Household participation (trailing 90 days)
CREATE VIEW v_participation AS
  SELECT
    COUNT(DISTINCT parishioner_id) AS households_shopping,
    (SELECT COUNT(*) FROM parishioners WHERE status='certified') AS households_certified
  FROM certified_purchases
  WHERE ordered_on >= datetime('now','-90 days');

-- Video coverage (trailing quarter)
CREATE VIEW v_video_coverage AS
  SELECT
    COUNT(*) AS deed_count,
    COUNT(video_id) AS deeds_with_video
  FROM deeds
  WHERE performed_on >= date('now','-90 days');

-- PAIX Witness revenue (trailing quarter, by platform)
CREATE VIEW v_paix_witness_revenue AS
  SELECT platform, SUM(net_to_caisse_dollars) AS revenue
  FROM platform_revenue
  WHERE period_end >= date('now','-90 days')
  GROUP BY platform;

-- Professional services (trailing quarter)
CREATE VIEW v_prof_services AS
  SELECT
    service_category,
    COUNT(DISTINCT provider_id) AS providers,
    SUM(market_value_dollars) AS market_value,
    SUM(credit_dollars_to_provider) AS credit_issued,
    SUM(net_value_to_caisse) AS net_to_caisse,
    AVG(walkaway_fraction) AS avg_walkaway
  FROM professional_services
  WHERE performed_on >= date('now','-90 days')
  GROUP BY service_category;
```

## Certification: the auto-approval algorithm

The steward's nightly queue should be a **3-minute review, not a 30-minute one**. The algorithm handles 95% of signups; the steward reviews the flagged 5%.

**Auto-approval rules** (all must pass to auto-approve):

1. Phone number is not blacklisted.
2. Phone number is not already associated with another `certified` account (prevents double-signup).
3. `display_name` non-empty and > 2 characters.
4. `claimed_parish` either empty OR matches a known-parish string in `data/known_parishes.json`.
5. Signup rate from this phone number's area code in the last 24h is below threshold (spam protection).

If all pass → auto-approve, generate code, send welcome SMS. If any fail → flag for steward review with reason.

**Flag reasons** (surfaced in steward queue):
- `AMBIGUOUS_PARISH`: claimed_parish doesn't match known list — verify by phone call.
- `HIGH_VOLUME_AREA_CODE`: possible spam wave — verify.
- `DUPLICATE_PHONE`: phone matches an existing account — merge or decline.
- `NAME_TOO_SHORT`: display_name < 3 chars — request full name.

Steward buttons on flagged rows: ✓ Approve · ? Follow-up · ✕ Decline.

## Video review: the second auto-approval loop

Video uploads run through an automated check before publication. Auto-review rules:

1. **Face count ≥ 2** in first 3 seconds (doer + witness or doer + beneficiary).
2. **Audio detected** and contains a witness line via speech-to-text (regex: `witness|attest|saw|swear|received`).
3. **No visible minors** OR `guardian_consent_given = 1`.
4. **File size and duration within bounds** (20–120 seconds, ≤ 500MB).

If all pass → `auto_review_passed = 1`; steward can approve for public in one click. If any fail → `auto_review_passed = 0`; steward reviews manually and either approves as unlisted-only, requests re-record, or rejects.

## The v1 order flow (manual, on purpose)

For the first hundred transactions, the steward places every Amazon order by hand. This is not a limitation; it is a **feature** — it forces human eyes on every redemption while trust is being built, exactly the way your grandfather's caisse would have handled every loan in its first year.

Flow:

1. **Parishioner** logs into shop, browses catalog, clicks "Request" on an item. Chooses payment mode: tokens, credit, dollars, or mix. Ledger checks balances; sufficient balances placed in escrow.
2. **Steward** receives an email: `"M.T.-1 requests grocery-week-family4 (6† or $90). Balance after: 12†. Fund cash after: $8,142."`
3. **Steward** clicks approve. Redemption row is written. Tokens/credit debited from escrow to spent.
4. **Steward** manually places the order on the parish Amazon Business account.
5. **Steward** pastes the Amazon order ID and actual dollars charged. Row updated. Fund cash debited.
6. **Nightly cron** recomputes `public/ledger.json`. Metrics tick.

At transaction #100, we evaluate whether to wire the [Amazon Business API](https://developer-docs.amazon.com/amazon-business/) for automated ordering. Not before.

## The vendor abstraction

Every `vendors/*.js` file exports the same interface:

```js
export async function placeOrder({ itemId, shipTo, tokens, expectedDollars }) {
  // returns { vendor_order_ref, actual_dollars, tracking_url? }
}

export async function verifyCovenantSigned() {
  // returns { signed_on, signatory, terms_version } or null
}
```

When a local grocer signs the parish covenant, we drop a `vendors/local_grocer_lenexa.js` implementing that interface, flip the `preferred_vendor` on the relevant catalog items, and no other code changes. **The parishioner sees the same shop; the money flows to a neighbor instead of Seattle.**

## The platform abstraction (PAIX Witness lane)

Every `platforms/*.js` file exports the same interface:

```js
export async function uploadVideo({ filePath, metadata, privacy }) {
  // returns { platform_video_id, url }
}

export async function fetchMonthlyRevenue({ month }) {
  // returns { gross, fees, net, period_start, period_end }
}
```

Currently: `youtube.js` (primary, [YouTube Data API](https://developers.google.com/youtube/v3)), `x.js` ([X API v2](https://developer.x.com/en/docs)), `meta.js` ([Meta Graph API](https://developers.facebook.com/docs/graph-api)). Adding a platform is one file plus a config entry.

## Hosting

- **Public shop + dashboard + deed wall**: GitHub Pages (free, publicly auditable, matches the user's `publish-to-github-pages` posture).
- **Steward pages**: same repo, gated by parish-issued auth (Auth0 free tier, or GitHub OAuth restricted to steward team).
- **Database**: SQLite on a small always-on host (Fly.io free tier or $5/mo VPS), with nightly encrypted backups to the parish's Google Drive.
- **Nightly cron**: GitHub Actions calling the host's `/recompute` endpoint.
- **Monthly revenue import**: GitHub Actions running `scripts/import_revenue.js` on the 1st.
- **Video source of truth**: YouTube (unlisted archive), with lightweight local metadata in `videos` table.

## Deliberate non-features

- **No parishioner-facing balances page.** A parishioner sees their balance only after signing in with the steward present in v1. Prevents public shaming, comparison, or coercion.
- **No leaderboard.** Ever.
- **No push notifications, no gamification.** The caisse is not a platform.
- **No AI in the loop that touches attestation.** Deeds and services are attested by human witnesses. Algorithms only *flag* for steward review; they never *credit* on their own.
- **No public beneficiary faces without explicit double opt-in.**

## What is buildable this week

The whole v1, honestly:

- **Day 1:** Fork storage shop, populate `shop.config.json` with 50 seed items, register YouTube/X/Meta accounts under `@paixwitness` handles.
- **Day 2:** SQLite schema (9 tables), seed with test data.
- **Day 3:** Public shop pages + steward queue/attest/approve/order pages.
- **Day 4:** Certification flow (public signup + SMS + steward auto-approval algorithm) + video capture flow (browser recorder + auto-review).
- **Day 5:** PAIX Witness cross-post pipeline (YouTube upload → X post → Meta post) + attribution links back to shop.
- **Day 6:** Nightly recompute + dashboard + Public Deed Wall.
- **Day 7:** Deploy to GitHub Pages + Fly.io. Frame the charter. Post it on the parish hall wall.

By day 8, the caisse is a real institution with a public ledger URL and a public deed wall you can hand to a Grand Knight.
