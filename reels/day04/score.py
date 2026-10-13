"""Original score + sound design for the SPOT Day 4 Reel (all synthesised).

Music: brighter road-trip feel in the Days 1–3 instrument family (C – G – Am – F).
SFX: indicator-style ticks under the 15 counter, a bell when it lands, road rumble
under the driving shots, whooshes on cuts, glass clinks for the bottles on the
dashboard, a soft bell per lesson, a drop "plip" on the dropper.
"""
import importlib.util
import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("day03_score", os.path.join(HERE, "..", "day03", "score.py"))
s3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(s3)
m = s3.m
SR = m.SR
rng = np.random.default_rng(44)

CHORDS = {
    "C": dict(bass=48, pad=[55, 60, 64, 67], arp=[67, 72, 76, 79]),
    "G": dict(bass=43, pad=[55, 59, 62, 67], arp=[67, 71, 74, 79]),
    "Am": dict(bass=45, pad=[57, 60, 64, 67], arp=[69, 72, 76, 79]),
    "F": dict(bass=41, pad=[53, 57, 60, 64], arp=[65, 69, 72, 76]),
    "Cmaj9": dict(bass=36, pad=[52, 55, 59, 62, 64], arp=[64, 67, 71, 74]),
}
s3.CHORDS.update(CHORDS)


def road_rumble(dur):
    """Low tyre/engine bed with slow movement, for the driving shots."""
    t = np.arange(int(dur * SR)) / SR
    x = m.lowpass(rng.standard_normal(len(t)), 220)
    x *= 1 + 0.25 * np.sin(2 * np.pi * 0.4 * t)
    return x * np.minimum(1, t / 0.4) * np.clip((dur - t) / 0.4, 0, 1)


def compose(starts, total, cues, path):
    s_hook, s_road, s_city, s_samples, s_lessons, s_dropper, s_dash, s_end = starts
    tr = m.Track(total + 0.5)

    # Hook: pad, indicator ticks while 0 → 15 counts up, bell + soft boom on landing.
    tr.add(0.0, m.pad(CHORDS["C"]["pad"], s_road + 0.4, attack=0.4), 0.26, verb=0.6)
    c0, c1 = cues["count"]
    last = -1
    for i in range(int((c1 + 0.05) * SR / 400)):
        t = i * 400 / SR
        if t < c0:
            continue
        k = 1 - (1 - min(1, (t - c0) / (c1 - c0))) ** 3
        step = int(k * 15)
        if step != last:
            tr.add(t, m.tick(90 if step % 2 else 95), 0.10, pan=0.25 if step % 2 else -0.25, verb=0.15)
            last = step
    tr.add(c1, m.bell(84), 0.12, verb=0.6)
    tr.add(c1, m.boom(1.4, 50), 0.22, verb=0.3)
    tr.add(s_road - 0.4, m.whoosh(0.55), 0.09, verb=0.2)

    # Road + city + samples: groove, road rumble underneath.
    bar = (s_lessons - s_road) / 4
    s3.bars(tr, s_road, ["C", "G", "Am", "F"], bar, keys_gain=0.14)
    tr.add(s_road, road_rumble(s_samples - s_road + 1.4), 0.10)
    for t in (s_city, s_samples, s_lessons):
        tr.add(t - 0.3, m.whoosh(0.45), 0.06, verb=0.2)
    tr.add(s_samples + 1.6, s3.glass_clink(1.0), 0.05, pan=-0.2, verb=0.4)
    tr.add(s_samples + 2.1, s3.glass_clink(1.15), 0.04, pan=0.25, verb=0.4)

    # Lessons: drums out, keys + pad, a bell as each lesson lands.
    half = (s_dropper - s_lessons) / 2
    for i, name in enumerate(["F", "G"]):
        ch = CHORDS[name]
        t0 = s_lessons + i * half
        tr.add(t0, m.pad(ch["pad"], half, attack=0.4, release=1.0, bright=1.2), 0.28, verb=0.6)
        tr.add(t0, m.bass(ch["bass"], half), 0.14)
    for i, d in enumerate(cues["lessons"]):
        tr.add(s_lessons + d, m.bell(79 + 3 * i, 2.4), 0.08, verb=0.6)
        tr.add(s_lessons + d, m.epiano(67 + 5 * i, 1.6, 0.7), 0.08, verb=0.5)

    # Dropper + dashboard: groove returns lightly, plip on the dropper.
    bar2 = (s_end - s_dropper) / 2
    s3.bars(tr, s_dropper, ["Am", "F"], bar2, keys_gain=0.13)
    tr.add(s_dropper + 0.6, s3.plip(), 0.14, verb=0.4)
    tr.add(s_dropper + 1.5, s3.plip(), 0.10, verb=0.4)
    tr.add(s_dash - 0.3, m.whoosh(0.45), 0.05, verb=0.2)
    tr.add(s_end - 0.5, m.whoosh(0.7), 0.07, verb=0.4)

    # End card: Cmaj9 resolve + bell on the logo.
    tail = total - s_end
    ch = CHORDS["Cmaj9"]
    tr.add(s_end, m.pad(ch["pad"], tail - 0.8, attack=0.6, release=1.0, bright=1.2), 0.32, verb=0.7)
    tr.add(s_end, m.bass(ch["bass"], tail), 0.14)
    for k, n in enumerate(ch["arp"]):
        tr.add(s_end + 0.15 + k * 0.16, m.epiano(n, 2.8, 0.75), 0.09, pan=-0.3 + 0.2 * k, verb=0.7)
    tr.add(s_end + 0.1, m.bell(84), 0.11, verb=0.8)

    # Mix (same chain as Days 1–3).
    wet = np.stack([m.reverb(tr.send[0], seed=11), m.reverb(tr.send[1], seed=23)])
    mix = tr.dry + 0.55 * wet
    mix = np.stack([m.highpass(mix[0], 45), m.highpass(mix[1], 45)])
    n = int(total * SR)
    mix = mix[:, :n]
    mix *= 10 ** (-17 / 20) / np.sqrt(np.mean(mix ** 2))
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))
    t = np.arange(n) / SR
    mix *= np.minimum(1, t / 0.03)
    mix *= np.clip((total - t) / 1.6, 0, 1) ** 1.5
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix.T * 32767).astype("<i2").tobytes())
    return path
