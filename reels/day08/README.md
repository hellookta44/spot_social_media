# SPOT — Day 8 Reel: "Why I started SPOT" (the typewritten letter)

| File | What it is |
|---|---|
| `out/spot_day08_reel.mp4` | Final reel with original music + sound design (1080×1920, 30 fps, 37.9s) |
| `out/spot_day08_reel_no_music.mp4` | Same reel, silent — for a trending sound or your own voice-over |
| `out/spot_day08_music.wav` | Score + sound design on its own (`score.py`) |
| `out/spot_day08_cover.jpg` | Designed cover (typed "WHY I STARTED SPOT." with a gold underline) — made by `reels/covers.py` |

A new format for the series, with no footage: the founder's letter is typed live on
cream paper (Courier typewriter face, uneven ink strikes, paper grain). The camera rides
the typing line, then pulls back to show the whole page on a dark desk, where a red pen
strikes "Big promises.", a gold pen underlines the key words, and the letter is signed in ink.

The letter is written from the series so far. **Check that the wording is true to you**
(edit `HEAD`, `PARAS` and `MARKS` in `render.py`; the timing and sounds follow the text).

## Storyboard

| Time | On screen | Sound |
|---|---|---|
| 0–1.5s | Close on the paper: **WHY I STARTED SPOT.** types out | Paper, typewriter keys, shimmer |
| 1.5–24s | The letter types line by line, the camera following: *Dear you, I started SPOT because I couldn't find skincare I actually trusted. Long labels. Big promises. Nobody explaining what's inside. So I asked questions. I tested 35 samples. I visited 15 factories. I said no. A lot. SPOT is the skincare I wanted to find: simple, honest, explained. If I wouldn't put it on my own skin, it doesn't go into SPOT.* | Keys, margin bell and carriage return on each line, quiet F-major piano |
| 24–26.5s | Camera pulls back: the whole letter on the desk | Riser, whoosh, soft boom; the groove and the piano hook come in |
| 26.5–31s | Red pen strikes **Big promises.**; gold pen underlines **actually trusted.**, **35 samples.**, **15 factories.**, **simple, honest, explained.** | Pen squeak + bell on each mark |
| 31–33.5s | Signed: *— Founder, SPOT* | Pen on paper |
| 33.5–38s | SPOT. end card: *Day 9: my skin story.* | Fmaj9 resolve + shimmer |

## Instagram caption

```
Day 8 of building SPOT. 🤍

I wrote you a letter.

Why start a skincare brand?
Because I couldn't find skincare I actually trusted.
Long labels. Big promises. Nobody explaining what's inside.

So I asked questions. 35 samples. 15 factories.
A lot of "no".

SPOT is the skincare I wanted to find:
simple, honest, explained.

If I wouldn't put it on my own skin,
it doesn't go into SPOT.

Tomorrow: my skin story.
Follow @shopspotbeauty for Day 9 ✨

#SPOTbeauty #Day8 #WhyIStarted #FounderStory #LetterFromTheFounder
#BuildingABrand #SkincareBrand #SkincareJourney #BehindTheBrand
#ComingSoon #SkincareProducts #SmallBusiness
```

## Re-render

```
python3 reels/day08/render.py
python3 reels/covers.py      # designed covers for every day
```
