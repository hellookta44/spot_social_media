#!/usr/bin/env python3
"""Download the Day 7 stock clips from Pexels (free licence) — one per hour slot.

Needs: network access to api.pexels.com + videos.pexels.com, and a Pexels API key
in the PEXELS_API_KEY environment variable (never commit the key).

Usage:  python3 reels/day07/fetch_pexels.py
Writes: reels/day07/footage/<slot>.mp4 and footage/credits.json (video URL + creator).
"""
import json
import os
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
FOOTAGE = os.path.join(HERE, "footage")

# slot name → search queries, tried in order until a good portrait clip is found
SLOTS = {
    "0600_sunrise": ["sunrise window bedroom", "morning sunrise window", "alarm clock morning"],
    "0730_coffee": ["pouring coffee close up", "coffee cup morning", "making coffee"],
    "0900_laptop": ["typing laptop close up", "hands typing keyboard", "working on laptop"],
    "1100_call": ["business phone call", "woman phone call office", "man on phone call"],
    "1300_lab": ["laboratory pipette", "cosmetic laboratory", "scientist lab test tube"],
    "1600_notes": ["writing notebook close up", "hand writing notes desk", "planning notebook"],
    "1900_drive": ["driving car city evening", "car traffic night city", "night drive city lights"],
    "2300_night": ["working late night laptop", "desk lamp night work", "laptop dark room"],
    "0000_city": ["city night timelapse", "city lights night", "night skyline"],
}


def api(query):
    url = "https://api.pexels.com/videos/search?" + urllib.parse.urlencode(
        {"query": query, "orientation": "portrait", "size": "medium", "per_page": 15})
    req = urllib.request.Request(url, headers={"Authorization": os.environ["PEXELS_API_KEY"],
                                               "User-Agent": "spot-reels/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def pick_file(video):
    """Best portrait MP4 at ~1080 wide (falls back to the closest above 720)."""
    files = [f for f in video.get("video_files", [])
             if f.get("file_type") == "video/mp4" and f.get("width") and f.get("height")
             and f["height"] > f["width"] and f["width"] >= 720]
    if not files:
        return None
    return min(files, key=lambda f: abs(f["width"] - 1080))


def main():
    if not os.environ.get("PEXELS_API_KEY"):
        sys.exit("PEXELS_API_KEY is not set (add it in the environment settings, then start a new session).")
    os.makedirs(FOOTAGE, exist_ok=True)
    credits, used = {}, set()
    for slot, queries in SLOTS.items():
        chosen = None
        for q in queries:
            for v in api(q).get("videos", []):
                f = pick_file(v)
                if f and v["id"] not in used and 5 <= v.get("duration", 0) <= 60:
                    chosen = (v, f, q)
                    break
            if chosen:
                break
        if not chosen:
            print(f"!! no portrait clip found for {slot}")
            continue
        v, f, q = chosen
        used.add(v["id"])
        dest = os.path.join(FOOTAGE, f"{slot}.mp4")
        req = urllib.request.Request(f["link"], headers={"User-Agent": "spot-reels/1.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as out:
            out.write(r.read())
        credits[slot] = {"query": q, "pexels_url": v["url"], "creator": v["user"]["name"],
                         "creator_url": v["user"]["url"], "duration": v["duration"],
                         "size": f"{f['width']}x{f['height']}"}
        print(f"{slot}: {v['url']} by {v['user']['name']} ({f['width']}x{f['height']}, {v['duration']}s)")
    with open(os.path.join(FOOTAGE, "credits.json"), "w") as fh:
        json.dump(credits, fh, indent=2)


if __name__ == "__main__":
    main()
