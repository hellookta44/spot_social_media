# SPOT — Day 5 Reel: "Behind the formula"

| File | What it is |
|---|---|
| `out/spot_day05_reel.mp4` | Final reel with original music + sound design (1080×1920, 30 fps, 27s) |
| `out/spot_day05_reel_no_music.mp4` | Same reel, silent — for a trending sound in Instagram |
| `out/spot_day05_music.wav` | Score + sound design on its own (`score.py`) |
| `out/spot_day05_cover.jpg` | Designed cover ("Behind the formula.") — made by `reels/covers.py` |

Three chapters: **01 Factory visits · 02 Formulation testing · 03 Chemist consultations.**

## Storyboard

| Time | Visual | On-screen text | Sound |
|---|---|---|---|
| 0–3s | Serum drop on skin (Pexels clip) | **What goes into one drop?** | Drop plip, shimmer, riser |
| 3–6s | Arriving at a factory (founder footage) | *01* FACTORY VISITS — **15 factories. Every one in person.** | Beat starts, car-door thud |
| 6–11s | Framed photo cards on cream: production line → raw materials → filling line (other brand's tube text blurred) | Production lines, checked up close. / Raw materials, inspected at the source. / Filling and hygiene, seen with our own eyes. | Camera shutter on each photo |
| 11–14s | Pink pipette macro | *02* FORMULATION TESTING — **Batch after batch, drop by drop.** | Piano hook enters, plips |
| 14–17s | Serum patted into skin (Pexels clip) | **How it absorbs. / How it feels. / How it lasts.** | Soft swish, ticks |
| 17–21s | Motion graphic: molecule drawing itself in gold | *03* CHEMIST CONSULTATIONS — **Every ingredient questioned.** *Every claim checked with chemists.* | Drums out, node ticks, glass clinks, riser |
| 21–23s | Serum drop on skin | **All this, before one drop reaches you.** | Impact + bell, full groove |
| 23–27s | SPOT. end card | *Day 6: what 29 no's look like.* | Resolve + shimmer |

Music: 96 BPM, Dm – Bb – F – C, piano hook doubled by bell, sidechain-pumped pad,
kick, snaps, shaker (same production as Day 2 v2; all synthesised).

**Media notes:** `serum_application_pexels.mp4` is a Pexels clip (free for commercial
use under the Pexels licence). The three factory photos were supplied as-is — make
sure SPOT has the right to use them; if they are not from your own visits, swap in
your own photos when you have them (same filenames, then re-render).

## Instagram caption

```
Day 5 of building SPOT. 🤍

What goes into one drop?

01 Factory visits — 15 factories, every one in person.
02 Formulation testing — batch after batch, drop by drop.
03 Chemist consultations — every ingredient questioned,
   every claim checked.

All this, before one drop reaches you.

Tomorrow: what 29 no's look like 👀
Follow @shopspotbeauty for Day 6 ✨

#SPOTbeauty #Day5 #BuildingABrand #SkincareBrand #SkincareJourney
#BehindTheBrand #FormulationTesting #CosmeticChemist #FactoryVisit
#ComingSoon #SkincareProducts #SmallBusiness
```

## Re-render

```
python3 reels/day05/render.py
python3 reels/covers.py      # designed covers for every day
```
