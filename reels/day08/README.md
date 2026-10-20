# SPOT — Day 8 Reel: "Why I started SPOT"

| File | What it is |
|---|---|
| `out/spot_day08_reel.mp4` | Final reel with original music + sound design (1080×1920, 30 fps, 34.5s) |
| `out/spot_day08_reel_no_music.mp4` | Same reel, silent — for a trending sound or your own voice-over |
| `out/spot_day08_music.wav` | Score + sound design on its own (`score.py`) |
| `out/spot_day08_cover.jpg` | Designed cover ("Why I started SPOT. a note from the founder.") — made by `reels/covers.py` |

A founder letter told in first person. All footage is real and none of it was used
in an earlier reel: three new sections of the founder clip (0.2s, 12.3s, 24.1s),
a city street from the road trip (19.4s) and the drive up to a factory (6.0s).

The "why" is written from the series so far. **Check the wording is true to you**
(edit the text in `render.py`). When you record yourself telling the story, swap
those clips into `SCENES` and use the no-music version under your voice.

## Storyboard

| Time | Visual | On-screen text | Sound |
|---|---|---|---|
| 0–3.5s | Founder to camera | **Why I started SPOT.** A note from the founder. | Solo piano, shimmer, bell |
| 3.5–8.5s | Cream letter card | THE PROBLEM — **I couldn't find skincare I actually trusted.** *Long labels. Big promises. Nobody explaining what's inside.* | Piano, pen tick per line |
| 8.5–12s | Founder holding the dropper | **So I started asking questions.** What's in it? Why? For whom? | Keys + shaker enter |
| 12–15s | City streets | **Every answer led somewhere new.** | Riser, impact, drums arrive |
| 15–18.5s | Drive up to a factory | **So I went looking myself.** 35 SAMPLES · 15 FACTORIES | Thud + bell on each number |
| 18.5–23s | Cream letter card | SO I'M BUILDING IT — **SPOT is the skincare I wanted to find.** *Simple. Honest. Explained.* | Piano hook, bell per word |
| 23–26.5s | Founder, close to camera | **Every ingredient. Every reason.** Explained, not hidden. | Full groove + hook |
| 26.5–30s | Cream card | *If I wouldn't put it on my own skin, it doesn't go into SPOT.* — FOUNDER, SPOT | Drums out, solo piano |
| 30–34.5s | SPOT. end card | *Day 9: my skin story.* | F major resolve + shimmer |

## Instagram caption

```
Day 8 of building SPOT. 🤍

People keep asking: why start a skincare brand?

Because I couldn't find skincare I actually trusted.
Long labels. Big promises. Nobody explaining what's inside.

So I started asking questions — and went looking myself.
35 samples. 15 factories. A lot of "no".

SPOT is the skincare I wanted to find:
simple, honest, explained.

If I wouldn't put it on my own skin,
it doesn't go into SPOT.

Tomorrow: my skin story.
Follow @shopspotbeauty for Day 9 ✨

#SPOTbeauty #Day8 #WhyIStarted #FounderStory #BuildingABrand
#SkincareBrand #SkincareJourney #BehindTheBrand #FounderJourney
#ComingSoon #SkincareProducts #SmallBusiness
```

## Re-render

```
python3 reels/day08/render.py
python3 reels/covers.py      # designed covers for every day
```
