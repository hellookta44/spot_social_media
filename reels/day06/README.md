# SPOT — Day 6 Reel: "What 29 no's look like"

| File | What it is |
|---|---|
| `out/spot_day06_reel.mp4` | Final reel with original music + sound effects (1080×1920, 30 fps, 22.5s) |
| `out/spot_day06_reel_no_music.mp4` | Same reel, silent — for a trending sound in Instagram |
| `out/spot_day06_music.wav` | Score + sound design on its own (`score.py`) |
| `out/spot_day06_cover.jpg` | Designed cover ("29 no's. and only 6 yes.") — made by `reels/covers.py` |

No new footage: earlier clips (new crops / unused sections) plus a data motion graphic.

## Storyboard

| Time | Visual | On-screen text | Sound |
|---|---|---|---|
| 0–3s | Rejected tubes (Day 1 clip), out of focus so no brand is readable | **What do 29 no's look like?** | Pad, two piano notes |
| 3–12s | Motion graphic: 35 dots land one by one (one dot = one sample received), counter to 35; then 29 fade and 6 turn gold and glide into a row | **0 → 35** samples received → **Only 6 made the shortlist.** That's about 1 in 6. | A tick per dot, impact on 35, downward "dim", six bell notes, chord bloom |
| 12–15s | Shortlist photo (label blurred) | **Those 6 are still being tested.** Not every one will make it. | Groove, glass clink |
| 15–18s | Pink pipette macro (unused section) | **Saying no is how we'll earn your yes.** | Drop plip |
| 18–22.5s | SPOT. end card | *Day 7: a day building SPOT.* | Resolve + bell |

## Instagram caption

```
Day 6 of building SPOT. 🤍

What do 29 no's look like?

Every dot is one sample we received and tested.
35 of them. 29 got a no. Only 6 made the shortlist — about 1 in 6.

And those 6 are still being tested.
Saying no is how we'll earn your yes.

Tomorrow: a day building SPOT, 6am to midnight.
Follow @shopspotbeauty for Day 7 ✨

#SPOTbeauty #Day6 #BuildingABrand #SkincareBrand #SkincareJourney
#BehindTheBrand #FounderJourney #QualityFirst #ComingSoon
#SkincareProducts #SmallBusiness #Skincare
```

## Re-render

```
python3 reels/day06/render.py
python3 reels/covers.py      # designed covers for every day
```
