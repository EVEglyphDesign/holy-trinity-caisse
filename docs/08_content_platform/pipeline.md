# PAIX Witness — Content Platform Pipeline

*Capture → Ingest → Cut → Distribute → Compile → Attribute → Report.*

*A Catholic content platform, built on the men's engine, powered by the works of the whole parish, aimed at the neighbor who has not yet been served.*

## What PAIX Witness is

PAIX Witness is the third turn of the Desjardins–McGivney wheel. Desjardins captured a Catholic people's **savings flow** and redirected it to their own; McGivney captured the same people's **insurance flow** and did likewise; PAIX Witness captures the **attention flow** the wider world now spends on short-form video, and redirects it, too, to the neighbor.

Concretely, PAIX Witness is:

- A shared publishing imprint (`@paixwitness`) on YouTube, X, Meta (Instagram + Facebook), and any successor platform;
- Under the shared imprint, one channel per participating parish's deed clips, cross-posted through the shared account;
- A content standard and evidence protocol that all participating parishes follow;
- A revenue-collection mechanic by which platform monetization — where it exists — flows back to each originating caisse's fund;
- A visible attribution — every public clip carries a link back to the originating parish's shop, so that attention becomes bread.

## The pipeline, end to end

```
┌───────────┐   ┌────────┐   ┌─────┐   ┌────────────┐   ┌─────────┐   ┌────────────┐   ┌────────┐
│  Capture  │──▶│ Ingest │──▶│ Cut │──▶│ Distribute │──▶│ Compile │──▶│ Attribute  │──▶│ Report │
└───────────┘   └────────┘   └─────┘   └────────────┘   └─────────┘   └────────────┘   └────────┘
     ▲                                                                                       │
     └───────────────────────────── feedback loop ──────────────────────────────────────────┘
```

## Stage 1 — Capture

**Who captures:** The witness, on their own phone. Not a videographer. Not a hired hand. **The one who signs the deed into the ledger is the one who films it.**

**The rule:** *One good deed. One witness. One hour. One token. One clip — if the neighbor allows it.*

**Standard clip length:** 20–120 seconds (per `shop.config.json → video_evidence_policy`). Long enough for the witness to speak their name and attest; short enough to travel.

**The three verbal beats every clip carries:**

1. **The witness names themselves.** *"This is [Knight's name], witnessing at Holy Trinity Parish."*
2. **The witness names the deed.** *"[Parishioner name] just spent an hour driving [neighbor's first name only, or "our neighbor"] to dialysis."*
3. **The consent line.** *"[Neighbor's first name / "Our neighbor"] has agreed to be part of this witness."* — OR the neighbor is out of frame, or blurred, and the witness says instead: *"Our neighbor's privacy is protected."*

If the clip is to be **publicly** posted (not merely unlisted), a fourth beat is added by the witness or the doer at capture time:

4. **The monetization consent line.** *"We consent to this clip being shared publicly under PAIX Witness."*

## Stage 2 — Ingest

**Where clips go on capture:** The steward's `/steward/publish` page, which accepts a direct browser upload from the witness's phone or a link to a phone-photos album entry.

**The auto-review runs immediately** (per `05_ledger_spec/README.md` § "Video review"):

| Check | What it verifies |
|---|---|
| Two-face rule | At least two faces detected in the first 3 seconds |
| Verbal witness line | Speech-to-text finds `witness|attest|saw|swear|received` |
| No minors OR guardian consent | Face-age estimation; guardian consent line detected if minor present |
| Duration and file bounds | 20–120s, ≤500MB, standard codec |

The ingest layer writes a `videos` row with `auto_review_passed`, `steward_review_status = 'pending'`, and stores the raw upload in the parish's private storage (Google Drive, iCloud, or Fly.io volume).

## Stage 3 — Cut

The standards editor — a role the steward or a designated Knight fills — reviews the queue on the `/steward/publish` page. For each clip, one of five decisions:

| Decision | What it does |
|---|---|
| **Approve public** | The clip goes to the public wall AND to the cross-post platforms |
| **Approve unlisted** | The clip is kept in the private archive; not published anywhere |
| **Approve public, blur beneficiary** | The clip is auto-blurred on the recipient's face, then published |
| **Request re-record** | The witness is asked to reshoot with a specific fix (better audio, add consent line, cover minor's face) |
| **Reject** | The clip is deleted from the archive; the deed itself remains in the ledger |

The standards editor's job is not artistic. It is **guardrail-tending.** The standards are:

- **What is never on video** (per `shop.config.json → video_evidence_policy.what_is_never_on_video`):
  - Financial coercion or debt-relief moments (a neighbor accepting money on camera)
  - Medical or hygiene intimacy
  - Minors without a spoken guardian consent line
  - A beneficiary in visible economic distress without face blur
  - Any deed where the beneficiary declined capture
- **What must always be there:** The witness's name, the deed named plainly, the consent line.
- **What must never be there:** A sponsor logo, a rating scale, a leaderboard, a "donate now" banner, or any language that turns the neighbor into a case study.

## Stage 4 — Distribute

Approved-public clips are cross-posted by `scripts/cross_post.js` through the three platform interfaces:

- **`platforms/youtube.js`** uploads the full 20–120s clip to `@paixwitness` on YouTube, tags it with the parish name and deed category, sets the description to include the standard attribution paragraph (below), adds it to the parish's channel playlist.
- **`platforms/x.js`** posts the clip natively to `@paixwitness` on X (X's algorithm favors native video over links), with a caption drawn from the deed description, and the attribution URL in the tweet body.
- **`platforms/meta.js`** posts the clip as a Reel on both `@paixwitness` on Instagram and `paixwitness` on Facebook, with the standard attribution in the caption.

**The standard attribution paragraph** (rendered in every platform's description/caption field):

> *A neighbor helped a neighbor at [Parish name] in [City, State]. One good deed, one witness, one hour, one token — that is the Rule of the caisse. Every hour donated feeds the parish's mutual-aid fund; every dollar the fund earns from attention like yours returns to the neighbor. Learn more or shop under the parish's roof at [shop.URL]. Vivat Jesus.*

Every clip's description ends with the same attribution shop URL — that is how the attention flow becomes a **bread flow.**

## Stage 5 — Compile

Weekly, `scripts/compile_weekly.js` produces:

- A **compilation reel** for YouTube (60–90s montage of that week's approved-public clips) — this is where the algorithmic reach lives, because compilation content outperforms single-deed content on YouTube Shorts;
- A **weekly digest post** for X threading three still frames + three clip links, with a summary line ("*This week at Holy Trinity: 12 hours of deeds attested by 8 witnesses. See them at ↓*");
- A **weekly IG Story sequence** for Meta, cross-linked to the reels.

Cross-parish compilations — for participating parishes across multiple dioceses — are the eventual reach lever. A single Holy Trinity parish's channel will grow slowly; a five-parish PAIX Witness compilation reel reaches meaningfully faster.

## Stage 6 — Attribute

Every public clip's description carries the attribution URL to the originating parish's shop. Every attention click on that URL is a candidate certification, a candidate donation, a candidate parishioner asking to be included.

Attribution is tracked plainly, in shop analytics — no third-party trackers, no pixels, no cross-site cookies. Just: which platform did the shop visitor come from, and did they certify, donate, or buy?

## Stage 7 — Report

**Monthly, on the first of the month,** `scripts/import_revenue.js` runs under GitHub Actions:

1. Pulls YouTube AdSense CSV for the prior month, matches by publish-date, credits gross and net revenue to `platform_revenue` with `platform = 'youtube'`;
2. Pulls X Creator Revenue Report, credits similarly;
3. Pulls Meta Reels Play bonus / Content Monetization report, credits similarly;
4. Sums into the ledger's fund solvency view;
5. Publishes the updated dashboard metric #7 (PAIX Witness revenue, trailing quarter, by platform).

**Every dollar earned belongs to the caisse's fund**, per Charter Article V. Not to the parishioners in the clips. Not to the videographers. Not to the standards editor. Not to PAIX overhead.

## Roles

*The men's engine builds and maintains; the parish drives it.*

| Role | Filled by | Load |
|---|---|---|
| **Witness / capturer** | Any parishioner present at a deed | ~1 min per deed |
| **Standards editor** | Steward, or a designated Knight | ~10 min per week, reviewing the queue |
| **Cross-post operator** | Same steward, or automation | Automated after Day-5 setup |
| **Monthly revenue importer** | GitHub Actions cron | 0 min ongoing |
| **Handles registrant** | The parish's tech-comfortable Knight | 1 hour, once, at setup |

**A single steward with a single hour a week can operate the entire PAIX Witness pipeline for a single-parish caisse.** Scale to a five-parish federation adds perhaps two hours a week; a standards editor and a cross-post operator can be different Knights by then.

## Guardrails (encoded, not proclaimed)

Everything in this list is either enforced by `shop.config.json` policy, by database constraint, or by the standards editor's five approval buttons. None of it is proclaimed on the channel itself:

- No sponsorship of individual clips by outside brands.
- No "donate now" call-to-action within a clip. Attribution is a link in the description, not a plea in the audio.
- No branded merchandise; no fundraising products; no product-placement in the frame.
- No case-study language about beneficiaries. Every neighbor is a first name, or "our neighbor."
- No leaderboard, ranking, or "top parishioner of the week" content.
- No political commentary, no partisan framing, no denunciation of anyone by name.
- No borrowed music the platform will demonetize; only the parish's own audio or platform-licensed music.
- No AI-generated faces, voices, or fabricated attestations.
- **The clip is a witness, not an advertisement. It sells nothing. It only shows what was done.**

The posture is quiet. The channel does not tell the world what it refuses to be. It simply is not those things, week after week.

## The one-week PAIX Witness setup

- **Day 1:** Register `@paixwitness` on YouTube, X, Instagram, Facebook. Register `paixwitness.example.org` (or similar).
- **Day 2:** Configure `platforms/youtube.js`, `platforms/x.js`, `platforms/meta.js` with API keys, using the `custom-credentials` pattern.
- **Day 3:** Build `/steward/publish` page with auto-review + five-button standards-editor decisions.
- **Day 4:** Build `scripts/cross_post.js` and `scripts/compile_weekly.js`.
- **Day 5:** Test end-to-end with three seed clips; verify auto-review, standards-editor flow, cross-post, attribution.
- **Day 6:** Standards-editor training walk-through with the steward, pastor, and a designated Knight.
- **Day 7:** First real deed captured, ingested, cut, published, compiled, attributed. The neighbor's face is protected. The Knight's name is spoken. The Rule holds. The wheel turns.
