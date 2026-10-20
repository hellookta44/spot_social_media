# SPOT — Day 8 Reel: "What goes into one bottle?"

| File | What it is |
|---|---|
| `out/spot_day08_reel.mp4` | Final reel with original music + sound design (1080×1920, 30 fps, 25.5s) |
| `out/spot_day08_reel_no_music.mp4` | Same reel, silent — for a trending sound in Instagram |
| `out/spot_day08_music.wav` | Score + sound design on its own (`score.py`) |
| `out/spot_day08_cover.jpg` | Designed cover ("What goes into one bottle?") — made by `reels/covers.py` |

Source: `footage/process.mov`, the 16s process clip (8 AI-generated stills with
captions printed on them). Each still is cropped to full-bleed 9:16, the printed
text is painted out, and the shot gets a film treatment: grade, upscale, slow dolly
and handheld drift, rack focus, live liquid motion on the pour and the mixing vat,
grain, vignette and bloom.

**Before posting:** these visuals are AI-generated, so switch on Instagram's
"AI info" label when you post (Meta asks for it on realistic AI video). The copy is
written as the journey of a formula, not as footage of a specific factory.

The previous Day 8 (typewritten founder letter) is kept in `reels/backlog/founder_letter/`.

## Storyboard

| Time | Shot | On-screen text | Sound |
|---|---|---|---|
| 0–3s | Ingredient pour (stream moving) | **What goes into one bottle?** The journey of a formula. | Room tone, liquid pour, piano |
| 3–6s | Mixing vat (liquid turning) | **Mixed slowly. Never rushed.** | Boom, pulse starts, mixer motor + swirl |
| 6–8.5s | Pipette over a test vial | **Tested before it's trusted.** | Drip, glass clink |
| 8.5–11s | Filling line | **Filled with care.** | Conveyor ticks, nozzle hiss, hook enters |
| 11–13.5s | Dropper caps | **Sealed to stay fresh.** | Cap screw clicks |
| 13.5–16s | Labelling | **Packaging comes last.** The formula always comes first. | Label feed |
| 16–18.5s | Finished bottles | **Simple. Honest. Explained.** | Glass touches |
| 18.5–21.5s | Hero bottle | **Skincare products, coming soon.** Follow the journey. | Drums out, shimmer |
| 21.5–25.5s | SPOT. end card | *Day 9: my skin story.* | Fmaj9 resolve |

## Instagram caption

```
Day 8 of building SPOT. 🤍

What goes into one bottle?

It starts with the ingredients.
Mixed slowly. Never rushed.
Tested before it's trusted.
Filled, sealed — and packaging comes last,
because the formula always comes first.

Simple. Honest. Explained.

Tomorrow: my skin story.
Follow @shopspotbeauty for Day 9 ✨

#SPOTbeauty #Day8 #BuildingABrand #SkincareBrand #SkincareJourney
#BehindTheBrand #HowItsMade #SkincareFormulation #ComingSoon
#SkincareProducts #SmallBusiness
```

## Re-render

```
python3 reels/day08/render.py
python3 reels/covers.py      # designed covers for every day
```
