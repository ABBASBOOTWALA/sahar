"""Whether a concept can calibrate a given detector.

The polysemy screen in polysemy.py asks a proportional question: what fraction
of a concept's documents predate its known origin? That screen was built against
a share-based detector and validated against it, and for that detector it works.

It gives no protection at all to a count-based detector, and the reason is
structural rather than a tuning problem. The screen's sensitivity is divided by
the concept's total literature; the detector's is not. A large concept can carry
a great deal of absolute junk and still show a negligible share. Genetic
algorithms carries 140 documents dated before Holland published, going back to
1828, and still passes the share screen at 0.047 per cent because it has 294,762
documents in total. Those 140 are enough to fire a three-document detector
twenty years early.

Several of them are traceable: five of the first ten pre-1930 hits come from the
Journal of the Franklin Institute, running since 1826, whose digitised back
catalogue has contaminated abstract fields. One is a real genetic algorithms
paper stamped 1912. This is metadata error, not polysemy, and a screen built for
polysemy was never going to see it.

So the admissibility test here is not another fixed rule. It runs the detector
itself over the years before the documented origin. If the detector fires there,
it is firing on something that cannot be the concept, and the concept cannot be
used to calibrate that detector.

The test therefore depends on the detector. A concept admissible for one setting
may be inadmissible for another, which is the point: a screen and a detector have
to be validated together, and swapping one invalidates the other.
"""
from . import threshold


def fires_before_origin(counts, totals, origin, c_ref, beta, sustain=threshold.SUSTAIN):
    """The detector's own verdict on the pre-origin window.

    Returns the year it wrongly fires, or None if it stays quiet as it should.
    """
    pre = {y: n for y, n in counts.items() if y < origin}
    if not pre:
        return None
    return threshold.onset(pre, totals, c_ref, beta, sustain=sustain)


def admissible(counts, totals, origin, c_ref, beta, sustain=threshold.SUSTAIN):
    return fires_before_origin(counts, totals, origin, c_ref, beta, sustain) is None


def audit(data, totals, c_ref, beta, sustain=threshold.SUSTAIN):
    """Which controls can legitimately calibrate this detector setting."""
    rows = []
    for name, (counts, origin) in data.items():
        bad = fires_before_origin(counts, totals, origin, c_ref, beta, sustain)
        rows.append({
            "concept": name,
            "origin": origin,
            "false_onset": bad,
            "admissible": bad is None,
            "pre_origin_docs": sum(n for y, n in counts.items() if y < origin),
        })
    return rows
