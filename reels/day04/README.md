# SPOT — Day 4 Reel: "On the road — 15 factories"

| File | What it is |
|---|---|
| `out/spot_day04_reel.mp4` | Final reel with original music + sound effects (1080×1920, 30 fps, 27s) |
| `out/spot_day04_reel_no_music.mp4` | Same reel, silent — for a trending sound in Instagram |
| `out/spot_day04_music.wav` | Score + sound design on its own (`score.py`) |
| `out/spot_day04_cover.jpg` | Cover image ("We visited 15 factories.") |

Same look as Day 3: Cormorant Garamond headlines (lining figures), Inter labels, DAY tag, end card.

## Storyboard

| Time | Footage | On-screen text | Sound |
|---|---|---|---|
| 0–3s | Hands on the steering wheel | We visited **0 → 15** factories. / Before choosing one. | Indicator-style ticks, bell + boom on 15 |
| 3–6s | Windscreen, tree-lined road | **Day 4 happened on the road.** / City to city. Factory to factory. | Groove starts, road rumble |
| 6–10s | City streets | **We don't pick a partner from a screen.** / We go and see for ourselves. | Road rumble, whoosh |
| 10–13s | Rural road → two samples on the dashboard | **The samples ride along.** / Tested in real life, not just the lab. | Glass clinks |
| 13–18s | Motion graphic (cream card) | **What 15 factories taught us:** 01 A great sample isn't a great batch. 02 Clean floors tell you more than brochures. 03 Good formulas can't be rushed. | Bell per lesson |
| 18–21s | Dropper in sunlight | **Only the best get to make SPOT.** | Drop plips |
| 21–23s | Sample on the dashboard | **The journey continues.** | Groove |
| 23–27s | SPOT. end card | *Day 5: behind the formula.* SKINCARE PRODUCTS · COMING SOON / @shopspotbeauty | Resolve + bell |

The three lessons were written for the reel; edit them in `LESSONS` in `render.py` if you want your own wording.

## Instagram caption

```
Day 4 of building SPOT. 🤍

We visited 15 factories before choosing one.

City to city, factory to factory — because we don't pick a
partner from a screen. We go and see for ourselves.

What 15 factories taught us:
01 A great sample isn't a great batch.
02 Clean floors tell you more than brochures.
03 Good formulas can't be rushed.

Only the best get to make SPOT.

Tomorrow: behind the formula 👀
Follow @shopspotbeauty for Day 5 ✨

#SPOTbeauty #Day4 #BuildingABrand #SkincareBrand #SkincareJourney
#BehindTheBrand #FounderJourney #Manufacturing #FactoryVisit
#ComingSoon #SkincareProducts #SmallBusiness
```

## Re-render

```
python3 reels/day04/render.py
python3 reels/covers.py      # designed covers for every day
```
