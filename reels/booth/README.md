# SPOT — "Our booth at Beauty Asia" (animated recap reel)

| File | What it is |
|---|---|
| `out/spot_booth_reel.mp4` | Recap reel with original music + sound design (1080×1920, 30 fps, 36s) |
| `out/spot_booth_reel_no_music.mp4` | Same reel, silent |
| `out/spot_booth_music.wav` | Score + sound design on its own (`score.py`) |
| `out/spot_booth_cover.jpg` | Cover (lit booth, "We had a booth at Beauty Asia.") |
| `out/spot_booth_design_board.jpg` | Labelled booth design board (3 m × 3 m) |

We had a booth at Beauty Asia but no footage, so the reel says so up front
("We were too busy talking to film it. So we drew it for you.") and retells the day
as an illustration. The booth is a drawn design (`booth.py`), not a photo of the real
booth — send a photo of the real one and the colours/layout can be matched.

## Storyboard

| Time | Visual | On-screen text | Sound |
|---|---|---|---|
| 0–4.5s | Dark hall; booth lights switch on; slow push-in | BEAUTY ASIA · OUR BOOTH — **We had a booth at Beauty Asia.** | Crowd, switch clunk + hum, pad swell, shimmer |
| 4.5–8s | Cream card | **We were too busy talking to film it.** *So we drew it for you.* | Piano notes |
| 8–12.5s | Two visitors walk up; staff waves | **Visitors came by.** Bubble: "Hi! Want to try it?" | Groove + hook, footsteps, bubble pop |
| 12.5–17s | Tester close-up: dropper → hand → rubbed in | **They tried it on their skin.** No pressure. Just the texture. | Drop plip, rub swish |
| 17–21.5s | Booth: visitor asks, staff answers | **And asked the best questions.** "What's inside?" → "Let us explain every ingredient." | Bubble pops |
| 21.5–25.5s | Waitlist tablet, phone scans the QR, gold check | **They joined the waitlist.** *You're on the list.* | Scanner beep, success chime |
| 25.5–29s | SPOT paper bag | **And took a little SPOT home.** | Bag rustle |
| 29–32s | Visitors walk away, staff waves | **Thank you for stopping by.** | Drums out, applause, footsteps |
| 32–36s | SPOT. end card | *Thank you, Beauty Asia.* | D major resolve + shimmer |

Booth design: backlit SPOT wall with "Skincare, explained.", oak slat wall, brass shelves
with unlabelled frosted bottles and SPOT boxes (no product reveal), white counter with a
gold edge, testers, mirror and a waitlist QR tablet, ink header fascia, track spots.

## Instagram caption

```
We had a booth at Beauty Asia. 🤍

We were too busy talking to film it — so we drew it for you.

Visitors came by, tried it on their skin, asked the best
questions ("what's inside?" was our favourite) and joined
the waitlist.

Thank you to everyone who stopped by.
Skincare products coming soon — follow @shopspotbeauty ✨

#SPOTbeauty #BeautyAsia #BuildingABrand #SkincareBrand #BeautyExpo
#BehindTheBrand #SkincareJourney #ComingSoon #SmallBusiness
```

## Re-render

```
python3 reels/booth/render.py
```
