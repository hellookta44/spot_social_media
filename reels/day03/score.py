"""Original score + sound design for the SPOT Day 3 Reel (all synthesised).

Music: same instrument family as Days 1–2, slower and more elegant (F – C – Dm – Bb).
SFX: shimmer on the title, cardboard thump, bubble-wrap crinkle and pops,
glass clinks on the bottles, drop "plips", a soft rubbing swish, whooshes on cuts.
"""
import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "day01"))
import music as m  # noqa: E402

SR = m.SR
rng = np.random.default_rng(31)

CHORDS = {
    "F": dict(bass=41, pad=[53, 57, 60, 64], arp=[65, 69, 72, 76]),
    "C": dict(bass=48, pad=[55, 60, 64, 67], arp=[67, 72, 76, 79]),
    "Dm": dict(bass=38, pad=[50, 57, 60, 65], arp=[62, 65, 69, 74]),
    "Bb": dict(bass=46, pad=[50, 53, 58, 62], arp=[62, 65, 70, 74]),
    "Fmaj9": dict(bass=41, pad=[52, 55, 57, 60, 64], arp=[64, 67, 69, 72]),
}
ARP = [0, 1, 2, 3, 2, 1, 2, 3]


# --------------------------------------------------------------------------- sound effects

def _t(dur):
    return np.arange(int(dur * SR)) / SR


def cardboard():
    t = _t(0.35)
    body = np.sin(2 * np.pi * (80 + 60 * np.exp(-t / 0.02)) * t) * np.exp(-t / 0.07)
    rustle = m.lowpass(rng.standard_normal(len(t)), 1800) * np.exp(-t / 0.05)
    return body * 0.8 + rustle * 0.6


def bubble_wrap(dur=1.4):
    t = _t(dur)
    y = np.zeros(len(t))
    crinkle = m.highpass(rng.standard_normal(len(t)), 2500)
    gate = np.zeros(len(t))
    for _ in range(int(dur * 70)):  # many tiny plastic crackles
        i = rng.integers(0, len(t) - 400)
        gate[i:i + 400] += rng.uniform(0.2, 1.0) * np.exp(-np.arange(400) / 60)
    y += crinkle * gate * 0.5
    for _ in range(4):  # a few distinct pops
        i = rng.integers(int(0.1 * SR), len(t) - 4000)
        k = np.arange(4000) / SR
        pop = m.spectral(rng.standard_normal(4000), lambda f: np.exp(-((np.log(np.maximum(f, 1) / 1300)) ** 2) / 0.3))
        y[i:i + 4000] += (pop * np.exp(-k / 0.006) * 2.5 + np.sin(2 * np.pi * 170 * k) * np.exp(-k / 0.015))
    return y * np.minimum(1, t / 0.05) * np.clip((dur - t) / 0.2, 0, 1)


def glass_clink(pitch=1.0):
    t = _t(1.2)
    y = sum(a * np.sin(2 * np.pi * f * pitch * t) * np.exp(-t / d)
            for f, a, d in ((2380, 1.0, 0.35), (3710, 0.6, 0.22), (5930, 0.4, 0.12), (8100, 0.2, 0.06)))
    return y * np.minimum(1, t / 0.0008)


def plip():
    t = _t(0.18)
    f = 520 + 900 * (1 - np.exp(-t / 0.03))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.045) * np.minimum(1, t / 0.002)


def rub_swish(dur, rate=1.8):
    t = _t(dur)
    x = m.lowpass(rng.standard_normal(len(t)), 1400)
    x = m.highpass(x, 250)
    env = np.abs(np.sin(np.pi * rate * t)) ** 1.5
    return x * env * np.minimum(1, t / 0.2) * np.clip((dur - t) / 0.3, 0, 1)


def shimmer(notes, gap=0.07):
    out = np.zeros(int((gap * len(notes) + 3.0) * SR))
    for i, n in enumerate(notes):
        b = m.bell(n, 2.8)
        s = int(i * gap * SR)
        out[s:s + len(b)] += b * (0.9 - 0.1 * i)
    return out


# --------------------------------------------------------------------------- score

def bars(tr, t0, names, bar, drums=True, keys_gain=0.13):
    beat = bar / 4
    for b, name in enumerate(names):
        tb = t0 + b * bar
        ch = CHORDS[name]
        tr.add(tb, m.pad(ch["pad"], bar, attack=0.4, release=0.8), 0.22, verb=0.5)
        tr.add(tb, m.bass(ch["bass"], beat * 3), 0.17)
        for k in range(8):
            tr.add(tb + k * beat / 2, m.epiano(ch["arp"][ARP[k]], 1.4, 0.85 if k % 2 == 0 else 0.6),
                   keys_gain, pan=-0.35 + 0.1 * k, verb=0.45)
        if drums:
            for q in range(4):
                tq = tb + q * beat
                if q in (0, 2):
                    tr.add(tq, m.kick(0.8), 0.28)
                else:
                    tr.add(tq, m.clap(0.8), 0.08, verb=0.3)
                tr.add(tq + beat / 2, m.hat(0.8), 0.04, pan=0.25)


def compose(starts, total, cues, path):
    s_hook, s_unbox, s_line, s_drop, s_rub, s_close, s_end = starts
    tr = m.Track(total + 0.5)

    # Hook: pad + shimmer as the title lands.
    tr.add(0.0, m.pad(CHORDS["F"]["pad"], s_unbox + 0.4, attack=0.6), 0.28, verb=0.6)
    tr.add(0.15, shimmer([77, 81, 84, 88, 89]), 0.06, pan=0.2, verb=0.7)
    tr.add(0.9, m.epiano(72, 2.0, 0.7), 0.10, verb=0.6)
    tr.add(s_unbox - 0.4, m.whoosh(0.55), 0.09, verb=0.2)

    # Unbox → lineup → drop → rub: four bars of soft groove (F – C – Dm – Bb).
    bar = (s_close - s_unbox) / 4
    bars(tr, s_unbox, ["F", "C", "Dm", "Bb"], bar)
    c0, c1, c2 = cues["unbox_cuts"]
    tr.add(s_unbox + c0 + 0.05, cardboard(), 0.45)
    tr.add(s_unbox + c1, bubble_wrap(1.4), 0.22, pan=-0.15)
    tr.add(s_unbox + c2 + 0.5, glass_clink(1.0), 0.06, pan=0.2, verb=0.4)
    for t in (s_line, s_drop, s_rub):
        tr.add(t - 0.3, m.whoosh(0.45), 0.05, verb=0.2)
    tr.add(s_line + 0.35, glass_clink(0.94), 0.05, pan=-0.25, verb=0.5)
    tr.add(s_line + 0.75, glass_clink(1.12), 0.04, pan=0.3, verb=0.5)
    for d in (1.45, 3.2):  # drops from the pipette onto the hand
        tr.add(s_drop + d, plip(), 0.16, verb=0.4)
    tr.add(s_rub, rub_swish(s_close - s_rub + 0.2), 0.05, pan=0.1, verb=0.2)
    for d in cues["rub_words"]:
        tr.add(s_rub + d + 0.1, m.tick(91), 0.07, verb=0.3)

    # Close: drums drop out, warm pad + slow keys, a soft swell.
    tr.add(s_close - 0.5, m.riser(0.5), 0.025, verb=0.4)
    tr.add(s_close, m.boom(2.0, 44), 0.12, verb=0.5)
    half = (s_end - s_close) / 2
    for i, name in enumerate(["Dm", "Bb"]):
        ch = CHORDS[name]
        t0 = s_close + i * half
        tr.add(t0, m.pad(ch["pad"], half, attack=0.5, release=1.2, bright=1.3), 0.30, verb=0.7)
        tr.add(t0, m.bass(ch["bass"], half), 0.14)
        for k, n in enumerate(ch["arp"]):
            tr.add(t0 + k * 0.14, m.epiano(n, 2.2, 0.75), 0.09, pan=-0.3 + 0.2 * k, verb=0.65)
    tr.add(s_end - 0.5, m.whoosh(0.7), 0.07, verb=0.4)

    # End card: Fmaj9 resolve + bell on the logo.
    tail = total - s_end
    ch = CHORDS["Fmaj9"]
    tr.add(s_end, m.pad(ch["pad"], tail - 0.8, attack=0.6, release=1.0, bright=1.2), 0.32, verb=0.7)
    tr.add(s_end, m.bass(ch["bass"], tail), 0.14)
    for k, n in enumerate(ch["arp"]):
        tr.add(s_end + 0.15 + k * 0.16, m.epiano(n, 2.8, 0.75), 0.09, pan=-0.3 + 0.2 * k, verb=0.7)
    tr.add(s_end + 0.1, m.bell(84), 0.11, verb=0.8)

    # Mix (same chain as Days 1–2).
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
