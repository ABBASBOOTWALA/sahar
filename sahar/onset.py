"""Onset detection, asymmetric by corpus size, and temporal relation."""
from . import config, openalex


def science_onset(counts, totals, p: config.OnsetParams = config.DEFAULT):
    """First year where the concept reaches a share of annual output and holds.

    Proportional because the index grows by orders of magnitude over the period;
    an absolute count would fire on the earliest metadata error.
    """
    years = sorted(y for y in counts if y >= config.MIN_YEAR and totals.get(y))
    if not years:
        return None
    ok = {y: counts[y] / totals[y] >= p.sci_share for y in years}
    for y in years:
        if all(ok.get(y + i, False) for i in range(p.sci_sustain)):
            return y
    return None


def art_onset(counts, p: config.OnsetParams = config.DEFAULT):
    """First year beginning a window that contains k substantive documents.

    Absolute because Leonardo publishes roughly 160 articles a year; a share
    threshold is unreachable for a concept appearing in two to sixteen documents
    per decade.
    """
    if not counts:
        return None
    for y in range(min(counts), max(counts) + 1):
        if sum(counts.get(y + i, 0) for i in range(p.art_window)) >= p.art_k:
            return y
    return None


def is_censored(onset):
    """An onset sitting exactly on the guard year is a floor, not a measurement."""
    return onset == config.MIN_YEAR


def relation(art, sci, p: config.OnsetParams = config.DEFAULT):
    if art is None and sci is None:
        return "neither"
    if art is None:
        return "science-only"
    if sci is None:
        return "art-only"
    d = sci - art
    if abs(d) <= p.simultaneous_tolerance:
        return f"simultaneous ({d:+d}y)"
    return ("art-first" if d > 0 else "science-first") + f" ({d:+d}y)"


def science_onset_for(concept, strategy, totals, p=config.DEFAULT):
    return science_onset(strategy.counts(concept), totals, p)
