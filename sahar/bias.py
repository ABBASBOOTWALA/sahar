"""Estimate and correct the systematic late bias on the science side.

Every control that passes the polysemy screen is measured LATE, never early:
information theory +4, computer graphics +4, fractal +12, genetic algorithms +12.
A bias that always points the same way is correctable in a way that random error
is not.

On the cause, our first guess was wrong and the data says so. We expected coverage
growth to make OLDER concepts measure later, since the early record is thinner.
The errors run the other way: origins in 1948 and 1963 are late by 4 years, while
both 1975 origins are late by 12.

The likely mechanism is the share threshold itself. Onset is defined as a share of
annual output, and annual output grows enormously over the period. In 1948 a
handful of papers was a large share of a small corpus. By 1975 the same concept
needs far more papers to clear the same share. So the threshold gets harder to
reach over time, which is the direction observed.

If that is right, a constant offset is the wrong correction and the threshold
should scale with corpus size instead. The offset below is a stopgap that halves
the error; it is not the fix.

Correction is estimated by leave-one-out, which matters here: with only four clean
controls, fitting and testing on the same points would be meaningless. Each
control's correction is estimated from the others and then tested on it.
"""
from statistics import mean

from . import concepts, onset, openalex, polysemy, resolve


def signed_errors(strategy=None, totals=None, screen=True):
    """measured minus documented, for each control. Positive means measured late."""
    strategy = strategy or resolve.PhraseField()
    totals = totals or openalex.total_counts()
    out = {}
    for c in concepts.CONTROLS:
        if screen:
            s = polysemy.screen(c.terms, c.science_origin, totals=totals)
            if s["verdict"] == "polysemy risk":
                continue
        m = onset.science_onset(strategy.counts(c), totals)
        if m is not None:
            out[c.name] = {"documented": c.science_origin, "measured": m,
                           "signed_error": m - c.science_origin}
    return out


def estimate(errors):
    """A single additive offset. Deliberately the simplest model that four points
    can support; anything richer would be fitting noise."""
    return mean(e["signed_error"] for e in errors.values())


def leave_one_out(errors):
    """Honest evaluation: correct each control using an offset estimated from the
    others only."""
    rows, raw, corrected = [], [], []
    for name, e in errors.items():
        others = {k: v for k, v in errors.items() if k != name}
        off = estimate(others)
        corr = e["measured"] - off
        rows.append({
            "concept": name,
            "documented": e["documented"],
            "measured": e["measured"],
            "offset_from_others": round(off, 1),
            "corrected": round(corr, 1),
            "error_before": abs(e["signed_error"]),
            "error_after": round(abs(corr - e["documented"]), 1),
        })
        raw.append(abs(e["signed_error"]))
        corrected.append(abs(corr - e["documented"]))
    return rows, mean(raw), mean(corrected)


def apply_offset(measured, offset):
    return None if measured is None else round(measured - offset)
