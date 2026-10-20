"""Original score + sound design for the SPOT Day 8 Reel: why I started SPOT (all synthesised).

A quieter, personal cue in F major: F – Dm – Bb – C. Solo piano and pad for the
founder's note and "the problem", keys + shaker while he asks questions, drums
arrive with the road, the piano hook carries the promise, then everything falls
back to piano for the signed line. SFX: a soft pen tick per problem line, thuds
under 35 and 15, a bell per promise word, shimmer on the logo.
"""
import importlib.util
import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("day02_score", os.path.join(HERE, "..", "day02", "score.py"))
s2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(s2)
s3, m = s2.s3, s2.m
SR = m.SR

s2.PROG[:] = [
    dict(bass=41, pad=[53, 57, 60, 65]),   # F
    dict(bass=38, pad=[53, 57, 62, 65]),   # Dm
    dict(bass=46, pad=[53, 58, 62, 65]),   # Bb
    dict(bass=48, pad=[55, 60, 64, 67]),   # C
]
HOOK = [72, None, 74, None, 77, 76, 72, None,   70, None, 72, None, 69, None, None, None]
s2.HOOK_B = [72, None, 74, None, 79, 77, 76, None,  77, None, 76, 72, 74, None, None, None]
ARP = [0, 2, 1, 3, 2, 1, 3, 2]


def piano_arps(tr, pads, t0, t1, gain=0.17, pad_gain=0.30):
    """Rubato-free solo piano: eighth-note broken chords over a soft pad."""
    b = 0
    while t0 + b * s2.BAR < t1 - 0.05:
        tb = t0 + b * s2.BAR
        ch = s2.PROG[b % 4]
        pads.add(tb, m.pad(ch["pad"], s2.BAR + 0.4, attack=0.5, release=0.8, bright=0.9), pad_gain, verb=0.7)
        tr.add(tb, m.epiano(ch["bass"] + 12, 2.4, 0.6), gain * 0.8, pan=-0.15, verb=0.6)
        for k, idx in enumerate(ARP):
            tn = tb + k * s2.BEAT / 2
            if tn >= t1:
                break
            tr.add(tn, m.epiano(ch["pad"][idx] + 12, 1.2, 0.55 + 0.1 * (k % 2 == 0)), gain, pan=0.15, verb=0.6)
        b += 1


def compose(starts, total, cues, path):
    s_hook, s_prob, s_ask, s_road, s_num, s_prom, s_every, s_sign, s_end = starts
    tr = m.Track(total + 0.5)
    pads = m.Track(total + 0.5)
    kicks = []

    # Founder's note + the problem: solo piano.
    tr.add(0.15, s3.shimmer([77, 81, 84, 89]), 0.04, pan=0.2, verb=0.7)
    piano_arps(tr, pads, 0.0, s_ask)
    tr.add(0.3, m.bell(84, 2.6), 0.05, verb=0.7)
    tr.add(s_prob - 0.3, m.whoosh(0.45), 0.04, verb=0.3)
    for i, d in enumerate(cues["problem"]):
        tr.add(s_prob + d, s2.pen_tick(), 0.09, pan=-0.2 + 0.2 * i, verb=0.25)
        tr.add(s_prob + d, m.epiano(76 - 2 * i, 1.4, 0.6), 0.06, verb=0.6)

    # Asking questions: keys + shaker, no drums yet.
    tr.add(s_ask - 0.3, m.whoosh(0.45), 0.05, verb=0.3)
    s2.groove(tr, pads, s_ask, s_road, drums=False, snaps=False, shake=True, hook=None, keys=True)
    tr.add(s_road - 0.9, m.riser(0.9), 0.04, verb=0.4)

    # Road → numbers → promise → every ingredient: full groove, hook on top.
    tr.add(s_road, m.boom(1.4, 41), 0.22, verb=0.35)
    kicks += s2.groove(tr, pads, s_road, s_prom, hook=None)
    kicks += s2.groove(tr, pads, s_prom, s_sign, hook=HOOK)
    for t in (s_road, s_num, s_prom, s_every):
        tr.add(t - 0.3, m.whoosh(0.45), 0.05, verb=0.2)
    for d in cues["numbers"]:
        tr.add(s_num + d, m.thud(), 0.14, verb=0.3)
        tr.add(s_num + d, m.bell(84, 2.0), 0.05, verb=0.6)
    for i, d in enumerate(cues["words"]):
        tr.add(s_prom + d, m.bell(81 + 3 * i, 2.4), 0.07, verb=0.6)

    # Signed line: drums out, back to solo piano.
    tr.add(s_sign - 0.4, m.whoosh(0.6), 0.06, verb=0.4)
    piano_arps(tr, pads, s_sign, s_end, gain=0.15)
    tr.add(s_sign + 1.3, m.bell(89, 2.6), 0.05, verb=0.7)

    # End card: Fmaj9 resolve + shimmer.
    tail = total - s_end
    pads.add(s_end, m.pad([53, 57, 60, 64, 67], tail - 0.6, attack=0.5, release=1.0, bright=1.2), 0.30, verb=0.7)
    tr.add(s_end, s2.sub(41, tail), 0.12)
    for j, n in enumerate([65, 69, 72, 76, 79]):
        tr.add(s_end + 0.12 + j * 0.13, m.epiano(n, 2.8, 0.75), 0.09, pan=-0.3 + 0.15 * j, verb=0.7)
    tr.add(s_end + 0.1, s3.shimmer([84, 88, 91, 96]), 0.05, verb=0.8)

    # Mix (same chain as Days 2, 5 and 7).
    n_all = tr.dry.shape[1]
    env = s2.sidechain(n_all, kicks)
    dry = tr.dry + pads.dry * env
    send = tr.send + pads.send * env
    wet = np.stack([m.reverb(send[0], seed=11), m.reverb(send[1], seed=23)])
    mix = dry + 0.5 * wet
    mix = np.stack([m.highpass(mix[0], 40), m.highpass(mix[1], 40)])
    n = int(total * SR)
    mix = mix[:, :n]
    mix *= 10 ** (-17 / 20) / np.sqrt(np.mean(mix ** 2))
    mix = np.tanh(mix * 1.15) / np.tanh(1.15)
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
