# SPOT — Day 2 Reel: "How a sample gets a yes"

| File | What it is |
|---|---|
| `out/spot_day02_reel.mp4` | Final reel with original background music (1080×1920, 30 fps, 25s) |
| `out/spot_day02_reel_no_music.mp4` | Same reel, silent — for adding a trending sound in Instagram |
| `out/spot_day02_music.wav` | The background score on its own (`score.py`) |
| `out/spot_day02_cover.jpg` | Cover image ("only 6") |

## Storyboard

| Time | Visual | On-screen text |
|---|---|---|
| 0–3s | Sample pouch photo, slow push-in (laptop screen blurred) | Sample #17582. / Every sample arrives like this. No brand. No name. Just a code. |
| 3–7s | Animated checklist (motion graphic) | Before any formulation gets a yes, it has to pass all five: Texture ✓ Absorption ✓ Feel on skin ✓ Ingredients ✓ Fragrance ✕ → REJECTED / One fail and it's out. |
| 7–11s | Animated close-up (`skin_test.py`): gold-collar dropper releases a drop onto the back of a hand, a fingertip rubs it in gently in circles, it absorbs | Then it goes on skin. / Applied. Rubbed in gently. How it absorbs. How it feels after. |
| 11–14s | Dropper clip | Pass every test? / Then it earns a second look. |
| 14–17s | Shortlist photo ("GEL Cleanser" label blurred) | From 700+ samples **700 → only 6** made the shortlist. |
| 17–20s | Shortlist photo, closer | Only the best will carry the SPOT name. / Which one would you pick? Tell us in the comments. |
| 20–25s | SPOT. end card | Day 3: the final cut. SKINCARE PRODUCTS · COMING SOON / Follow the journey @shopspotbeauty |

## Instagram caption

```
Day 2 of building SPOT. 🤍

Every sample that reaches us arrives the same way —
no brand, no name, just a code.

Then the formulation has to pass five checks: texture,
absorption, feel on skin, ingredients and fragrance.
Fail one, and it's out.

From 700+ samples, only 6 made the shortlist.
Only the best will carry the SPOT name.

Which one would you pick? Tell us below 👇
Day 3: the final cut. Follow @shopspotbeauty ✨

#SPOTbeauty #Day2 #BuildingABrand #SkincareBrand #SkincareJourney
#BehindTheBrand #FounderJourney #SmallBusiness #ComingSoon
#SkincareProducts #SkincareLaunch #QualityFirst #Skincare
```

## Posting tips

- Post 1–2 days after Day 1, same time of day.
- Use `out/spot_day02_cover.jpg` as the cover so the grid shows "only 6".
- Reply to every "which one" comment — it boosts reach and sets up Day 3.

## Re-render

```
python3 reels/day02/render.py
python3 reels/covers.py      # designed covers for every day
```

Uses the Day 1 helpers in `reels/day01/render.py` and instruments in `reels/day01/music.py`.
