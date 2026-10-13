"""Original score + sound design for the SPOT Day 5 Reel (all synthesised).

The 700-dot graphic drives the sound: a patter of soft ticks that speeds up as
the dots land, an impact when the counter hits 700+, a downward "dim" as the
rejected dots fade, six bell notes as the shortlist turns gold, and a chord
bloom as the six gather. Music follows in the Days 1–4 instrument family.
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
rng = np.random.default_rng(55)

CHORDS = {
    "Am": dict(bass=45, pad=[57, 60, 64, 67], arp=[69, 72, 76, 79]),
    "F": dict(bass=41, pad=[53, 57, 60, 64], arp=[65, 69, 72, 76]),
    "C": dict(bass=48, pad=[55, 60, 64, 67], arp=[67, 72, 76, 79]),
    "G": dict(bass=43, pad=[55, 59, 62, 67], arp=[67, 71, 74, 79]),
    "Cmaj9": dict(bass=36, pad=[52, 55, 59, 62, 64], arp=[64, 67, 71, 74]),
}
s3.CHORDS.update(CHORDS)


def dim_sweep(dur=0.9):
    """Downward filtered sweep: the 694 rejected dots fading out."""
    t = np.arange(int(dur * SR)) / SR
    f = 900 * np.exp(-t / 0.35) + 120
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    air = m.lowpass(rng.standard_normal(len(t)), 1500)
    return (tone * 0.6 + air * 0.4) * np.sin(np.pi * t / dur) ** 2


def compose(starts, total, cues, path):
    s_hook, s_dots, s_short, s_line, s_end = starts
    tr = m.Track(total + 0.5)

    # Hook: low pad, a question hanging.
    tr.add(0.0, m.pad(CHORDS["Am"]["pad"], s_dots + 0.5, attack=0.5), 0.26, verb=0.6)
    tr.add(0.4, m.epiano(76, 2.2, 0.7), 0.10, verb=0.6)
    tr.add(1.2, m.epiano(72, 2.2, 0.6), 0.08, verb=0.6)
    tr.add(s_dots - 0.4, m.whoosh(0.55), 0.09, verb=0.2)

    # Dots: tick patter that thickens as they land (every 4th dot sounds), riser, impact on 700+.
    times = cues["dot_times"]
    for i, t in enumerate(times[::4]):
        tr.add(s_dots + t, m.tick(88 + (i % 5) * 2), 0.05, pan=float(rng.uniform(-0.6, 0.6)), verb=0.15)
    fill_end = times[-1]
    tr.add(s_dots + 0.5, m.pad(CHORDS["Am"]["pad"], fill_end, attack=1.5), 0.16, verb=0.6)
    tr.add(s_dots + fill_end - 1.6, m.riser(1.6), 0.05, verb=0.4)
    tr.add(s_dots + fill_end + 0.02, m.boom(1.6, 48), 0.40, verb=0.35)
    tr.add(s_dots + fill_end + 0.02, m.thud(), 0.30, verb=0.2)

    # Fade + shortlist: dim sweep, then six bell notes (pentatonic), bloom as they gather.
    fade = cues["fade"]
    tr.add(s_dots + fade - 0.1, dim_sweep(), 0.12, verb=0.4)
    for j, note in enumerate([76, 79, 81, 84, 86, 88]):
        tr.add(s_dots + fade + 0.15 + j * 0.09, m.bell(note, 2.4), 0.07, pan=-0.5 + 0.2 * j, verb=0.7)
    g0, g1 = cues["gather"]
    tr.add(s_dots + g0, m.whoosh(g1 - g0 + 0.2), 0.06, verb=0.4)
    ch = CHORDS["C"]
    tr.add(s_dots + g1 - 0.1, m.pad(ch["pad"], s_short - s_dots - g1 + 0.6, attack=0.3, bright=1.3), 0.26, verb=0.7)
    for k, n in enumerate(ch["arp"]):
        tr.add(s_dots + g1 + k * 0.12, m.epiano(n, 2.0, 0.75), 0.09, pan=-0.3 + 0.2 * k, verb=0.6)

    # Shortlist photo + the line: groove (F – G | Am – F).
    bar = (s_end - s_short) / 4
    s3.bars(tr, s_short, ["F", "G", "Am", "F"], bar, keys_gain=0.13)
    tr.add(s_short + 0.4, s3.glass_clink(1.0), 0.04, pan=0.2, verb=0.5)
    tr.add(s_line - 0.3, m.whoosh(0.45), 0.06, verb=0.2)
    tr.add(s_line + 0.9, s3.plip(), 0.12, verb=0.4)
    tr.add(s_end - 0.5, m.whoosh(0.7), 0.07, verb=0.4)

    # End card: Cmaj9 resolve + bell.
    tail = total - s_end
    ch = CHORDS["Cmaj9"]
    tr.add(s_end, m.pad(ch["pad"], tail - 0.8, attack=0.6, release=1.0, bright=1.2), 0.32, verb=0.7)
    tr.add(s_end, m.bass(ch["bass"], tail), 0.14)
    for k, n in enumerate(ch["arp"]):
        tr.add(s_end + 0.15 + k * 0.16, m.epiano(n, 2.8, 0.75), 0.09, pan=-0.3 + 0.2 * k, verb=0.7)
    tr.add(s_end + 0.1, m.bell(84), 0.11, verb=0.8)

    # Mix (same chain as Days 1–4).
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
