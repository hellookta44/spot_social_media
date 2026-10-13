# SPOT — Day 2 Reel: "How a sample gets a yes"

| File | What it is |
|---|---|
| `out/spot_day02_reel.mp4` | Final reel (v2) with original music + sound design (1080×1920, 30 fps, 26s) |
| `out/spot_day02_reel_no_music.mp4` | Same reel, silent — for a trending sound in Instagram |
| `out/spot_day02_music.wav` | Score + sound design on its own (`score.py`) |
| `out/spot_day02_cover.jpg` | Designed cover ("Only 6 made the shortlist.") — made by `reels/covers.py` |

Version 2 follows the 30-day plan (hook "Sample #17582.") in the Days 3–5 look:
Cormorant Garamond headlines, cream motion graphics, and real skin-test footage
(from `reels/day03/footage`) instead of the earlier drawn animation.

## Storyboard

| Time | Visual | On-screen text | Sound |
|---|---|---|---|
| 0–3s | Sample pouch photo, push-in (laptop screen blurred) | **Sample #17582.** Every sample arrives like this. No brand. No name. Just a code. | Pouch crinkle, low hit + shimmer, riser |
| 3–8s | Cream checklist: gold numerals, ticks drawing in, Fragrance struck through in red + REJECTED stamp | **Before any formulation gets a yes, it must pass all five.** 01 Texture · 02 Absorption · 03 Feel on skin · 04 Ingredients · 05 Fragrance ✕ / *One fail and it's out.* | Groove starts; pen tick per check, wrong-note blip, thud + paper slap on the stamp |
| 8–11s | Founder inspecting the bottle and dropper | **Then we test it ourselves.** Look. Smell. Texture. | Piano hook enters, drop plip |
| 11–14s | Fingertip testing on the hand | **On skin. / Rubbed in. / Felt after.** (word by word) | Rubbing swish, soft ticks |
| 14–16s | Pink pipette macro | **Pass every test?** *Then it earns a second look.* | Breakdown: piano hook alone, riser |
| 16–19s | Shortlist photo ("GEL Cleanser" label blurred) | From 35 samples, **35 → only 6** *made the shortlist.* | Falling ticks, impact + bell on "only 6", full groove |
| 19–22s | Shortlist photo, closer | **Only the best will carry the SPOT name.** Which one would you pick? Tell us in the comments. | Groove + hook |
| 22–26s | SPOT. end card | *Day 3: the final cut.* SKINCARE PRODUCTS · COMING SOON / @shopspotbeauty | Fmaj9 resolve + shimmer |

Music: 96 BPM, F – Am – Dm – Bb, a 2-bar piano hook doubled by a soft bell,
sidechain-pumped pad, kick, finger snaps and shaker (all synthesised, no samples).

## Instagram caption

```
Day 2 of building SPOT. 🤍

Every sample that reaches us arrives the same way —
no brand, no name, just a code.

Then the formulation has to pass five checks: texture,
absorption, feel on skin, ingredients and fragrance.
Fail one, and it's out.

From 35 samples, only 6 made the shortlist.
Only the best will carry the SPOT name.

Which one would you pick? Tell us below 👇
Day 3: the final cut. Follow @shopspotbeauty ✨

#SPOTbeauty #Day2 #BuildingABrand #SkincareBrand #SkincareJourney
#BehindTheBrand #FounderJourney #SmallBusiness #ComingSoon
#SkincareProducts #SkincareLaunch #QualityFirst #Skincare
```

## Posting tips

- Post 1–2 days after Day 1, same time of day.
- Use `out/spot_day02_cover.jpg` as the cover (designed series cover).
- Reply to every "which one" comment — it boosts reach and sets up Day 3.

## Re-render

```
python3 reels/day02/render.py
python3 reels/covers.py      # designed covers for every day
```

Uses helpers from `reels/day03/render.py` / `reels/day01/render.py` and instruments from `reels/day01/music.py`.
