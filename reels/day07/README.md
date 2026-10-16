# SPOT — Day 7 Reel: "Inside Beauty Asia"

| File | What it is |
|---|---|
| `out/spot_day07_reel.mp4` | Final reel with original music + sound design (1080×1920, 30 fps, 25s) |
| `out/spot_day07_reel_no_music.mp4` | Same reel, silent — for a trending sound in Instagram |
| `out/spot_day07_music.wav` | Score + sound design on its own (`score.py`) |
| `out/spot_day07_cover.jpg` | Designed cover ("Beauty Asia. a day at the expo.") — made by `reels/covers.py` |

All footage is the founder's own from the expo (2 clips, 4 photos).

## Storyboard

| Time | Visual | On-screen text | Sound |
|---|---|---|---|
| 0–3s | Arriving at the expo centre | **We went to Beauty Asia.** To learn from the whole industry. | Pad, shimmer, crowd fades in |
| 3–6s | Founder walking the hall (photo) | **Hall after hall. Brand after brand.** | Beat starts, footsteps |
| 6–9s | Ingredient-supplier booth (photo) | **We met ingredient suppliers.** Where does every raw material come from? | Piano hook enters |
| 9–11s | Face-scanning skin analyzer (slow motion) | **Saw the newest skin tech.** | Scanner beep + sweep |
| 11–14s | Founder taking notes at a booth (photo) | **Asked questions. Took notes.** Lots of notes. | Pen tick, scribble |
| 14–18s | Cream card | **What Beauty Asia taught us:** 01 Everyone sells. Few explain. 02 People ask what's inside, not just the price. 03 Simple, honest formulas stand out. | Drums out, bell per lesson |
| 18–21s | Founder walking with bags (photo) | **Came home with ideas.** (and a few bags) | Impact, groove + hook, bag rustle |
| 21–25s | SPOT. end card | *Day 8: why I started SPOT.* | A major resolve + shimmer |

The three lessons were written for the reel; edit `LESSONS` in `render.py` for your own wording.

## Instagram caption

```
Day 7 of building SPOT. 🤍

We went to Beauty Asia — to learn from the whole industry.

Hall after hall, brand after brand. We met ingredient
suppliers, saw the newest skin tech, asked a lot of
questions and took even more notes.

What Beauty Asia taught us:
01 Everyone sells. Few explain.
02 People ask what's inside, not just the price.
03 Simple, honest formulas stand out.

Came home with ideas (and a few bags).

Tomorrow: why I started SPOT.
Follow @shopspotbeauty for Day 8 ✨

#SPOTbeauty #Day7 #BeautyAsia #BuildingABrand #SkincareBrand
#SkincareJourney #BehindTheBrand #FounderJourney #BeautyExpo
#ComingSoon #SkincareProducts #SmallBusiness
```

## Re-render

```
python3 reels/day07/render.py
python3 reels/covers.py      # designed covers for every day
```
