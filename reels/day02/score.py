"""Original background score for the SPOT Day 2 Reel.

Same instruments as Day 1 (reels/day01/music.py) so the series sounds related,
but a brighter C major progression and new cues: a tick on every checklist
tick, a thud on the REJECTED stamp, a falling countdown, and a hit on "only 6".
"""
import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "day01"))
import music as m  # noqa: E402

SR = m.SR

CHORDS = {
    "C": dict(bass=48, pad=[55, 60, 64, 67], arp=[67, 72, 76, 79]),
    "G": dict(bass=43, pad=[55, 59, 62, 67], arp=[67, 71, 74, 79]),
    "Am": dict(bass=45, pad=[57, 60, 64, 67], arp=[69, 72, 76, 79]),
    "F": dict(bass=41, pad=[53, 57, 60, 64], arp=[65, 69, 72, 76]),
    "Fmaj7": dict(bass=41, pad=[52, 57, 60, 64], arp=[64, 69, 72, 76]),
    "Cmaj9": dict(bass=36, pad=[52, 55, 59, 62, 64], arp=[64, 67, 71, 74]),
}
ARP = [0, 1, 2, 3, 2, 1, 2, 3]


def groove(tr, t0, bars, names, bar, drums=True):
    beat = bar / 4
    for b in range(bars):
        tb = t0 + b * bar
        ch = CHORDS[names[b % len(names)]]
        tr.add(tb, m.pad(ch["pad"], bar, attack=0.3, release=0.6), 0.20, verb=0.4)
        tr.add(tb, m.bass(ch["bass"], beat * 2.5), 0.20)
        tr.add(tb + beat * 2.5, m.bass(ch["bass"], beat * 1.5), 0.15)
        for k in range(8):
            vel = 0.85 if k % 2 == 0 else 0.6
            tr.add(tb + k * beat / 2, m.epiano(ch["arp"][ARP[k]], 1.2, vel), 0.14,
                   pan=-0.35 + 0.1 * k, verb=0.35)
        if drums:
            for q in range(4):
                tq = tb + q * beat
                tr.add(tq, m.kick() if q in (0, 2) else m.clap(), 0.34 if q in (0, 2) else 0.10,
                       verb=0 if q in (0, 2) else 0.25)
                tr.add(tq + beat / 2, m.hat(), 0.05, pan=0.25)


def compose(starts, total, cues, path):
    s1, s2, s3, s4, s5, s6 = starts
    tr = m.Track(total + 0.5)

    # Scene 1: pouch — soft intro, pad + sparse keys, a bell on the sample number.
    tr.add(0.0, m.pad(CHORDS["C"]["pad"], s2 + 0.3, attack=0.5), 0.28, verb=0.5)
    tr.add(0.2, m.bell(84), 0.10, verb=0.7)
    for k, note in enumerate([72, 76, 79, 84]):
        tr.add(1.1 + k * 0.32, m.epiano(note, 1.6, 0.7), 0.10, pan=-0.3 + 0.2 * k, verb=0.5)
    tr.add(s2 - 0.45, m.whoosh(0.6), 0.10, verb=0.2)

    # Scenes 2–3: groove under the checklist and dropper (C – G – Am – F).
    bar = (s4 - s2) / 4
    groove(tr, s2, 4, ["C", "G", "Am", "F"], bar)
    for i, tc in enumerate(cues["check_times"]):
        if i == cues["fail_index"]:
            tr.add(s2 + tc, m.tick(84), 0.14, verb=0.2)          # lower, "wrong" blip
        else:
            tr.add(s2 + tc, m.tick(96 + 2 * i), 0.12, pan=0.2, verb=0.2)
    tr.add(s2 + cues["stamp"], m.thud(), 0.45, verb=0.25)
    tr.add(s3 - 0.35, m.whoosh(0.5), 0.06, verb=0.2)

    # Scene 4: countdown 700 -> 6, falling ticks, hit on landing.
    c0, c1 = cues["count"]
    tr.add(s4, m.pad(CHORDS["Am"]["pad"], s5 - s4 + 0.3, attack=0.4), 0.22, verb=0.5)
    last = -1
    for i in range(int((c1 + 0.05) * SR / 400)):
        t = i * 400 / SR
        if t < c0:
            continue
        k = 1 - (1 - min(1, (t - c0) / (c1 - c0))) ** 3
        step = int(k * 22)
        if step != last:
            tr.add(s4 + t, m.tick(100 - step), 0.09, pan=0.3 if step % 2 else -0.3, verb=0.15)
            last = step
    tr.add(s4 + c1, m.boom(), 0.36, verb=0.35)
    tr.add(s4 + c1, m.bell(81), 0.12, verb=0.6)

    # Scene 5: drums return lightly for the question.
    groove(tr, s5, 2, ["Fmaj7", "G"], (s6 - s5) / 2, drums=False)
    for q in range(4):
        tr.add(s5 + q * (s6 - s5) / 4, m.kick(0.6), 0.22)
    tr.add(s6 - 0.5, m.whoosh(0.7), 0.07, verb=0.4)

    # Scene 6: Cmaj9 resolve on the logo.
    tail = total - s6
    ch = CHORDS["Cmaj9"]
    tr.add(s6, m.pad(ch["pad"], tail - 0.8, attack=0.6, release=1.0, bright=1.2), 0.32, verb=0.7)
    tr.add(s6, m.bass(ch["bass"], tail), 0.15)
    for k, note in enumerate(ch["arp"]):
        tr.add(s6 + 0.15 + k * 0.16, m.epiano(note, 2.8, 0.75), 0.09, pan=-0.3 + 0.2 * k, verb=0.7)
    tr.add(s6 + 0.1, m.bell(84), 0.12, verb=0.8)

    # Mix (same chain as Day 1).
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
