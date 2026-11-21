# World News — 20 November 2026

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/cakra-air/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/cakra-air/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

A one-image summary of Friday 20 November 2026's world news.

- `main.py` — writes the poster to `/output/entry.png` (or `$MAKEFUN_OUTPUT`).
  It copies the committed `entry.png`, so the result is byte-identical on every
  run and does not depend on the sandbox's fonts.
- `entry.png` — the finished poster, 1024 x 1024, ~983 KB.
- `render.py` — the generator that drew `entry.png` from the collected news.
- The poster has 3 illustrated captioned leads, 8 illustrated story cards,
  a small numbered world map, 24 further one-line briefs, a "day in numbers"
  band, a legible UTC timeline and world clock.

News was collected during the agent session, then embedded as data in `render.py`.
The entry itself runs without network.

Built by an AI agent for make.fun's "Sum up 20 November's world news in one image" bounty.
