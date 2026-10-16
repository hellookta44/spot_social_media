# SPOT — Backlog reel: "A day building SPOT" (6am to midnight)

Not scheduled yet (Day 7 became the Beauty Asia expo). When you use it, change
`make_tag("07")`, the folder name and the end-card teaser in `render.py` to the real day.

**Status: edit, music and cover are ready; the stock footage is downloaded at render time.**

All footage for this reel is new: free-licence Pexels stock clips, one per hour.
Nothing from Days 1–6 is reused.

## Render (needs Pexels access)

1. Environment settings → Network access: allow `pexels.com`, `www.pexels.com`,
   `videos.pexels.com`, `api.pexels.com`.
2. Environment settings → add your free Pexels API key (pexels.com/api) as
   `PEXELS_API_KEY`. Never commit the key.
3. In a new session:

```
python3 reels/backlog/day_in_the_life/fetch_pexels.py   # downloads 9 portrait clips + footage/credits.json
python3 reels/backlog/day_in_the_life/render.py
python3 reels/covers.py
```

Check `footage/credits.json` and swap any clip you don't like (same filename) before rendering.

## Storyboard

A gold analog clock + serif time stamp ticks forward at every cut (hands sweep to the new time).

| Clock | Pexels search (slot) | Line | Sound |
|---|---|---|---|
| 6:00 AM | sunrise window (`0600_sunrise`) | *The day starts before the city does.* | Alarm chime, ticking clock begins |
| 7:30 AM | pouring coffee (`0730_coffee`) | *Coffee first. Then the list.* | Coffee pour, groove starts |
| 9:00 AM | typing laptop (`0900_laptop`) | *Emails to manufacturers.* | Keyboard typing, piano hook enters |
| 11:00 AM | phone call (`1100_call`) | *A call with our chemist.* | Phone buzz |
| 1:00 PM | laboratory pipette (`1300_lab`) | *Back to the formulas.* | Glass clink, drop |
| 4:00 PM | writing notebook (`1600_notes`) | *Notes. Decisions. More notes.* | Pen scratch |
| 7:00 PM | night drive (`1900_drive`) | *On the road again.* | Passing car |
| 11:00 PM | working late (`2300_night`) | *Still at it.* | Drums out, piano alone |
| 12:00 AM | city at night (`0000_city`) | *Tomorrow, we go again.* | Bell |
| — | SPOT. end card | *Day 8: why I started SPOT.* | Gmaj9 resolve + shimmer |

Music: 96 BPM, G – D – Em – C, clock-tick pulse on every eighth note, piano hook + bell,
sidechain pad, kick, snaps, shaker (all synthesised).

## Instagram caption

```
Day 7 of building SPOT. 🤍

6am to midnight — this is what a day building a skincare brand looks like.

Coffee. Emails to manufacturers. Calls with our chemist.
Back to the formulas. Notes, decisions, more notes.
On the road again. Still at it at 11pm.

Tomorrow, we go again.

Day 8: why I started SPOT.
Follow @shopspotbeauty ✨

#SPOTbeauty #Day7 #BuildingABrand #DayInTheLife #FounderLife
#SkincareBrand #SkincareJourney #BehindTheBrand #ComingSoon
#SkincareProducts #SmallBusiness #Startup
```

Credits: footage from Pexels (pexels.com); creators listed in `footage/credits.json`.
Crediting is optional under the Pexels licence but appreciated.
