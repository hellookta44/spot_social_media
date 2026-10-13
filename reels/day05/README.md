# SPOT — Day 5 Reel: "What 700 no's look like"

| File | What it is |
|---|---|
| `out/spot_day05_reel.mp4` | Final reel with original music + sound effects (1080×1920, 30 fps, 22.5s) |
| `out/spot_day05_reel_no_music.mp4` | Same reel, silent — for a trending sound in Instagram |
| `out/spot_day05_music.wav` | Score + sound design on its own (`score.py`) |
| `out/spot_day05_cover.jpg` | Designed cover ("700 no's. and only 6 yes.") — made by `reels/covers.py` |

No new footage: earlier clips (new crops / unused sections) plus a data motion graphic.

## Storyboard

| Time | Visual | On-screen text | Sound |
|---|---|---|---|
| 0–3s | Rejected tubes (Day 1 clip), out of focus so no brand is readable | **What do 700 no's look like?** | Pad, two piano notes |
| 3–12s | Motion graphic: 700 dots land one by one (one dot = one sample), counter to 700+; then all fade except 6 gold dots, which glide into a row | **0 → 700+** samples rejected → **Only 6 made the shortlist.** That's less than 1%. | Tick patter that speeds up, impact on 700+, downward "dim", six bell notes, chord bloom |
| 12–15s | Shortlist photo (label blurred) | **Those 6 are still being tested.** Not every one will make it. | Groove, glass clink |
| 15–18s | Pink pipette macro (unused section) | **Saying no is how we'll earn your yes.** | Drop plip |
| 18–22.5s | SPOT. end card | *Day 6: a day building SPOT.* | Resolve + bell |

## Instagram caption

```
Day 5 of building SPOT. 🤍

What do 700 no's look like?

Every dot is one sample we tested and turned down.
700+ of them. Only 6 made the shortlist — less than 1%.

And those 6 are still being tested.
Saying no is how we'll earn your yes.

Tomorrow: a day building SPOT, 6am to midnight.
Follow @shopspotbeauty for Day 6 ✨

#SPOTbeauty #Day5 #BuildingABrand #SkincareBrand #SkincareJourney
#BehindTheBrand #FounderJourney #QualityFirst #ComingSoon
#SkincareProducts #SmallBusiness #Skincare
```

## Re-render

```
python3 reels/day05/render.py
python3 reels/covers.py      # designed covers for every day
```
