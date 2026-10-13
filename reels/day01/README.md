# SPOT — Day 1 Reel: "700+ samples rejected"

| File | What it is |
|---|---|
| `out/spot_day01_reel.mp4` | Final reel with original background music (1080×1920, 30 fps, 22s) |
| `out/spot_day01_reel_no_music.mp4` | Same reel, silent — use this if you'd rather add a trending sound in Instagram |
| `out/spot_day01_music.wav` | The background score on its own |
| `out/spot_day01_cover.jpg` | Cover image (the 700+ hook) |

## Music

`music.py` composes an original score in code (no samples, no third-party
music), cut to the edit: ticks under the 700+ counter, an impact when it lands,
a soft beat on the road, a thud on every REJECTED stamp, drums drop out for the
"your skin deserves" line, and a warm resolve on the logo.

## Storyboard

| Time | Footage | On-screen text |
|---|---|---|
| 0–3s | Rejected sample tubes | We said no to **0 → 700+** samples rejected. |
| 3–7s | On the road | Day 1 didn't start in a lab. / It started on the road — meeting manufacturer after manufacturer. |
| 7–11s | Sample package at desk | Sample after sample landed on our desk. / Every one opened. Every one tested. |
| 11–14s | Sample tubes + REJECTED stamps | Most of them? / "Good enough" wasn't good enough. |
| 14–18s | Dropper bottle | Because your skin deserves the one that's right. / Not the one that's easy. |
| 18–22s | SPOT. end card | Skincare products. COMING SOON / Follow the journey from Day 1 @shopspotbeauty |

## Instagram caption

```
Day 1 of building SPOT. 🤍

Before we ever said "yes", we said "no" — more than 700 times.

700+ samples. Countless manufacturers. Weeks on the road.
Every sample opened, tested, and judged against one question:
would we put this on our own skin?

Most of them didn't make the cut.

Our skincare products are coming soon — and we're
taking you along for every step of the journey.

Follow @shopspotbeauty so you don't miss Day 2. ✨

#SPOTbeauty #Day1 #BuildingABrand #SkincareBrand #SkincareJourney
#SmallBusiness #FounderJourney #BehindTheBrand #ComingSoon
#SkincareProducts #SkincareLaunch #BrandStory #Startup #Skincare
```

## Posting tips

- Post `spot_day01_reel.mp4` as is, or post `spot_day01_reel_no_music.mp4` with a trending sound for extra reach.
- Use `out/spot_day01_cover.jpg` as the cover so the grid shows the "700+" hook.
- Post 7–9pm local time; pin a comment like "Guess how many samples we rejected on Day 2? 👀".

## Re-render

```
python3 reels/day01/render.py
python3 reels/covers.py      # designed covers for every day
```

All text, timings and clip choices live in `render.py` (see `SCENES`).
