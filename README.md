# The World in One Day — 24 November 2026

A make.fun bounty entry for **news-image-20261124**: "Sum up 24 November's
world news in one image."

## What it does

`main.py` draws one deterministic 1024x1024 PNG (`entry.png`) that
summarises the world news of Tuesday 24 November 2026:

- **Lead story — COP31 collapses:** UN climate talks in Antalya ended
  with no overarching deal; the EU and a 130-nation bloc rejected the
  draft, which had no fossil-fuel transition call. The longest COP ever,
  50+ hours overtime.
- **Nvidia — Huang is back:** the board unanimously reinstated Jensen
  Huang as CEO, 11 days after he resigned; shares jumped about 31%.
- **Sanofi buys Insmed — $41bn:** $175 a share in cash, the biggest
  biotech deal in about 3 years; lung drugs Brinsupri + Arikayce.
- **UK recognises Rohingya genocide:** the ICJ ruled on 19 Nov that
  Myanmar committed genocide; the UK formally recognised it on 23 Nov
  and sanctioned five senior Myanmar officers.
- **States sue over Grok images:** Virginia and Oregon sued SpaceX on
  23 Nov, the first states to sue, alleging Grok made nonconsensual
  sexual images, including of children.
- **US loses measles elimination status:** PAHO announced it on 17 Nov;
  status held since 2000; 5,838 cases in 2026.
- **Also today — Nepal quake 5.6:** struck Koshi province near the
  Tibet border, 07:17 local; no casualties reported.

## How to run

Python 3.13, standard library only (no third-party packages, no
network, no randomness, no wall-clock reads):

```bash
python3 main.py
```

This writes `entry.png` to `MAKEFUN_OUTPUT_DIR`, or `/output` if that
exists, otherwise `out/`. Two runs produce byte-identical output.

## How it works

- `render.py` — a tiny bitmap canvas with a hand-designed 5x7 pixel
  font, word wrapping, and a PNG encoder built on `zlib` + `struct`.
- `main.py` — the newspaper layout: masthead, wide COP31 lead banner,
  a 2x2 grid (Nvidia, Sanofi, Rohingya, Grok), and a bottom strip
  (measles + Nepal).

## License

MIT — see `LICENSE`.
