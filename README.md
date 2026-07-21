> **⚑ Arrivals register at the front door.**
> If you were sent here from a public post, a mention, or a professional referral, please [register your arrival](https://github.com/EVEglyphDesign/eveglyph-arrivals/issues/new?template=arrival.yml) at [github.com/EVEglyphDesign](https://github.com/EVEglyphDesign) before continuing. Ninety seconds. Public. Timestamped. Screeners, agents, publicists, journalists, engineers, and principals all use the same door.
>
> *Compelled engagement, not asked engagement.*

---
# Holy Trinity Caisse

A parish-scale mutual-aid economy under the umbrella of PAIX.

**One good deed. One witness. One hour. One token.**

## Live site

The current parish site is published from this repository via GitHub Pages.

## This is a template

This repository is intended to be forked, parish by parish, diocese by diocese. Each caisse is a durable node on GitHub. The Charter, ledger schema, and shop configuration are shared canon; the parish name, working groups, and members change.

## Structure

- `docs/` — the founding packet (Charter, history, dashboard spec, economic model, ledger spec, Knights letter, certification flow, content pipeline)
- `build.py` — Python markdown → HTML builder (no dependencies beyond Python 3 stdlib + `markdown` package)
- HTML files at the repo root — the static site served by GitHub Pages
- `.nojekyll` — tells GitHub Pages to serve files as-is

## Rebuild

```
pip install markdown
python3 build.py
```

## Fork this

To start a new caisse for another parish:

1. Fork this repository
2. Change `docs/PACKET.md` and `docs/01_charter/charter.md` to name your parish
3. Rebuild with `python3 build.py`
4. Enable GitHub Pages on the fork (Settings → Pages → Source: main / root)

## Governance

Under PAIX. Safety first, betterment second.
