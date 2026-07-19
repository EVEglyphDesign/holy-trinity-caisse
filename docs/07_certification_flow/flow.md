# Certification & Enrollment Flow — Holy Trinity Caisse

*The Knights build the engine. Every working group of the parish uses it. The ledger, in time, will show who is doing the most.*

The Knights of Columbus build the caisse's operational spine — the certification queue, the auto-approval algorithm, the steward's nightly review, the professional-services enrollment desk. Once the spine is built, **every working group of the parish can contribute what it has to contribute**:

- The **Knights** contribute the engine itself, and the ongoing witness work.
- The **education and formation groups** — catechists, teachers, tutors, youth ministers, sacramental-prep leaders — contribute hours of learning, attested by a fellow group member.
- The **social-development groups** — St. Vincent de Paul conferences, hospitality committees, bereavement teams, welcome ministries, elder-care volunteers — contribute hours of accompaniment, hospitality, and care.
- The **healthcare professionals** — physicians, dentists, nurses, therapists, and allied health — contribute hours of their trade at market rate, choosing their own walk-away fraction.
- The **trades and legal-and-financial professionals** — plumbers, electricians, contractors, attorneys, CPAs, translators, IT — contribute the same way.
- The **young parishioners** contribute hours of service attested by a teacher, coach, or ministry lead — credited to their household's balance.
- The **elders** contribute by witnessing — signing deeds, blessing the ledger with their names, and offering their long-held trades as they always have.

Every working group's hour is one hour, and every group's contribution is on the same ledger. This document describes how any parishioner — with a phone number and a name — walks through the door.

The caisse does not sort parishioners into categories the wider world uses. It sorts by **what a parishioner brings** — an hour of driving, an hour of tutoring, an hour of the trade they were trained in, an hour of witnessing another's hour. The dashboard's ninth metric will, over time, show which working groups are carrying the caisse. That answer is the ledger's to give, not this document's to guess.

## Part 1 — The parishioner's side (30 seconds)

**The certification page:** `shop.holytrinitycaisse.example.org/certify`

Single form, three fields:

```
[ Your name ]
[ Your phone number ]
[ The parish you belong to — start typing ]
```

Below the form, one line:

> *By clicking Request Certification, you consent to receive one SMS from the caisse steward's queue. The parish will confirm you against its roll and welcome you into the shop, usually within one day.*

One button: **Request Certification.**

That is the entire parishioner-facing certification UX. No email. No password. No verification code (yet). No terms-of-service scroll. No cookie banner beyond what the law requires. **The parish is not Amazon; it does not need to know more about a soul than her name, her number, and the parish she belongs to.**

Behind that click, the system:

1. Inserts a row into `parishioners` with `status = 'pending'`, `joined_on = today`.
2. Runs the five auto-approval checks (§ Part 3 below).
3. If all pass — auto-approves; generates the code (`HT-XXXX-NAME`); sends the welcome SMS immediately.
4. If any fail — flags for the steward's morning queue with the flag reason attached to the row.

The parishioner sees, on the confirmation screen:

> *Welcome. If you were auto-approved, your code is on its way by text now. Otherwise, a steward will call you within a day to confirm.*

## Part 2 — The steward's nightly queue (3 minutes)

**The steward page:** `shop.holytrinitycaisse.example.org/steward/queue` (auth-gated)

The queue is meant to be reviewed once a day, at whatever hour suits the steward — typically after dinner, before the ledger's nightly recompute at 23:00 CT. It is intentionally a **3-minute review, not a 30-minute one.**

The queue view lists only flagged rows. Each row shows:

```
Marie-Therese Kane · (913) 555-0142 · Holy Trinity, Lenexa
Joined: 2026-07-19 · Flag: AMBIGUOUS_PARISH — "Holy Trinity" (12 US parishes carry this name)
[ ✓ Approve ]   [ ? Follow-up ]   [ ✕ Decline ]
```

Auto-approved rows do **not** appear in the queue. They appear only in the daily digest email the steward receives at 07:00 CT:

> *Overnight the caisse auto-approved 6 parishioners: Kane, Landry, Boucher, Comeau, Doucet, LeBlanc. Certification code registry is at [link].*
>
> *Flagged for your review this morning: 2. Queue: [link].*

**The 3-minute discipline:** Auto-approval handles ~95% of signups; the steward reviews the ~5% flagged; the whole task fits in a coffee break.

## Part 3 — The auto-approval algorithm

Five checks, all must pass to auto-approve:

| # | Check | Fail flag |
|---|---|---|
| 1 | Phone number is not blacklisted | `BLACKLISTED_PHONE` |
| 2 | Phone number is not already associated with another `certified` account | `DUPLICATE_PHONE` |
| 3 | `display_name` non-empty AND length ≥ 3 characters AND contains at least one space | `NAME_TOO_SHORT` |
| 4 | `claimed_parish` either empty OR matches a known-parish string in `data/known_parishes.json` (fuzzy match, Levenshtein ≤ 3) | `AMBIGUOUS_PARISH` |
| 5 | Signup rate from this phone number's area code in the last 24h is below threshold (default: 10/day/area-code) | `HIGH_VOLUME_AREA_CODE` |

Rows with **no fail flags** are auto-approved:

```sql
UPDATE parishioners
SET status = 'certified',
    code = format('HT-%s-%s', short_id, upper(last_name)),
    certified_on = CURRENT_TIMESTAMP,
    auto_approved = 1
WHERE id = ?;
```

Rows with **any fail flag** remain `status = 'pending'`, with the flag(s) attached to `notes`.

**The philosophy:** The algorithm has one job — to remove obvious tedium from the steward's evening. It does not decide who is a Catholic, who belongs to Holy Trinity, or who is worthy. It only sorts the certain from the ambiguous, and hands the ambiguous to a human.

## Part 4 — The welcome SMS

Auto-approval sends immediately:

> *Welcome, Marie-Therese. You are now certified with the Holy Trinity Caisse. Your shopping code is **HT-4291-KANE** — enter it at checkout on shop.holytrinitycaisse.example.org so your ordinary purchases quietly serve the fund. Save this text. Vivat Jesus.*

Steward-approval sends after the ✓ Approve click:

> *Marie-Therese, this is [Steward name] from Holy Trinity. Welcome. Your shopping code is **HT-4291-KANE** — enter it at checkout on shop.holytrinitycaisse.example.org. Call the parish office if you have any question. Vivat Jesus.*

Follow-up sends after the ? Follow-up click:

> *Marie-Therese, this is [Steward name] from Holy Trinity Caisse. I would like to confirm your registration by phone at your convenience. Please call the parish office at [number]. Vivat Jesus.*

Decline sends only if the steward opts to notify. Most declines (spam, duplicate, blacklist hits) are silent.

## Part 5 — Professional-services enrollment (a sub-flow)

For parishioners who have a trade to offer — attorney, CPA, physician, dentist, plumber, electrician, tutor, therapist, translator, IT consultant, tradesperson, designer, and so on — there is a second, quiet enrollment step, taken separately after certification.

**The professional's page:** `shop.holytrinitycaisse.example.org/steward/prof_service/enroll` (accessible from any certified parishioner's account)

Form fields:

```
Credential type ...................... [ dropdown: JD/Bar, MD, CPA, licensed trade, etc. ]
Credential reference (bar #, license #, etc.) ... [ optional ]
Jurisdiction .......................... [ optional ]
Standard market rate ($/hr) ........... [ e.g. $150 ]
Default walk-away band ................ [ radio: 0%  10%  20%  30% ]
Notes ................................. [ e.g. "willing to take 3 tax returns per year" ]
```

Below the walk-away band selector, one line of explanation:

> *You choose your own measure. Zero means the whole hour is a gift. Ten, twenty, or thirty percent means the caisse issues you credit equal to that fraction of the market rate of the service, which your household may spend at the shop. The remainder is booked as your gift to the mission. **This is your household's answer to what your household can spare.***

**The professional's page is not public.** Parishioners see only the general caisse; only certified parishioners with an enrolled credential see the professional-services log.

### The service log

When the professional performs a service for another parishioner, either the professional or a steward logs it:

```
Provider ........................ [ Marie-Therese Kane, CPA ]
Service category ................ [ dropdown ]
Service description ............. [ "2026 tax return prep, Franco family" ]
Recipient ....................... [ certified parishioner OR the parish itself ]
Witness ......................... [ recipient OR a steward ]
Hours ........................... [ 2.0 ]
Market rate ($/hr) .............. [ auto-filled from credential; overridable within ±20% ]
Walk-away this service .......... [ 0%  10%  20%  30% — default from credential, overridable per service ]
```

The ledger computes:

```
market_value_dollars     = hours × market_rate
credit_to_provider       = market_value × walkaway_fraction
net_to_caisse            = market_value − credit_to_provider
```

An IRS receipt is generated for the provider automatically, using the language templated in `shop.config.json → professional_services_policy.irs_receipt_template`.

### Enrollment auto-approval

Professional-service enrollment is **never** auto-approved. Every credential must be verified by a steward (or a delegated professional-services steward, ideally a Knight who is himself an attorney or CPA) against the credential's public licensing registry — the state bar, the state board of accountancy, the state medical board, the city licensing office. This verification is one phone call or one web lookup per enrollment, done once per lifetime of the credential.

The verified professional's row is stamped with `verified_on` and `verified_by`, and the professional can log services from that moment forward.

## Part 6 — What the flow does not do

*Guardrails: encoded, not proclaimed.*

- The flow does not ask about race, income, immigration status, marital status, orientation, or any category the wider world uses to sort people into rent-tiers. **The parishioner is a soul, not a segment.**
- The flow does not resell, monetize, or cross-market the phone numbers it collects. There is no data broker in the loop.
- The flow does not accept payment for faster certification. Every parishioner waits the same short wait.
- The flow does not surface disputes between parishioners. If two parishioners are in disagreement over a deed, a service, or a token, the pastor and the steward hear it privately. The caisse does not adjudicate; it records.
- The flow does not sort professionals into tiers, ratings, reviews, or leaderboards. Every professional's hour is one hour; every professional's fee is her own conscience's answer.
- The flow does not host third-party ads, tracking pixels, or affiliate codes anywhere on the shop pages, the steward pages, or the deed wall. **The caisse is the neighbor's page, not the market's.**

These are the shape of the engine, not the slogan on its side. The caisse's posture is quiet: it does not become a rent-taker, a tax collector, an arbitrator, a decider of winners and losers, a seller of attention, or a racer of yachts. **What it is not, it need not name. It is enough that it does not become those things.**

## Part 7 — The one-week rollout

- **Day 1:** Steward's queue page + auto-approval algorithm live on staging.
- **Day 2:** Public `/certify` page live; SMS provider configured (Twilio or a diocesan SMS vendor).
- **Day 3:** Seed `data/known_parishes.json` with the diocese's parish roll.
- **Day 4:** Test end-to-end: five test signups, three auto-approved, two flagged.
- **Day 5:** Professional-services `/enroll` sub-flow live; five test enrollments processed by the steward.
- **Day 6:** Steward-training walk-through with the pastor and the first designated Knight witness.
- **Day 7:** Announcement in the parish bulletin. The engine is on. The parish drives.
