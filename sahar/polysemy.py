"""Automatic polysemy detection, derived from the cultural tracer method.

The idea comes from a property of dated cultural phrases: anything occurring
before the release date cannot be a reference, so the pre-release period measures
the false-positive rate for free.

That generalises. For any concept with a documented origin, usage before the
origin is by definition a *different sense of the same words*. So the pre-origin
rate is a polysemy detector, and it needs no language model.

Validated against the six science controls: it flags holography (570 pre-1948
hits, the "holographic wills" of probate law) and artificial life (vitalism
papers of 1907 and 1911), which are precisely the two concepts whose onsets the
pilot measured wrongly. The four it passes are the four the pilot measured
correctly.

This matters because it converts polysemy from something discovered by hand,
after a result looks strange, into something screened for before analysis.
"""
from statistics import mean

from . import openalex

PRE_WINDOW = 20
CLEAN = 100.0      # lift at or above this: no detectable prior sense
SUSPECT = 20.0     # below this: the term was already in use, treat with care


def screen(terms, origin_year, exclude_leonardo=True, totals=None):
    """Return a polysemy assessment for a term set with a documented origin."""
    totals = totals or openalex.total_counts()
    filters = [f"title_and_abstract.search:{openalex.phrase_query(terms)}"]
    if exclude_leonardo:
        filters.append(openalex.exclude_leonardo())

    counts = openalex.year_counts(filters)
    rates = {y: 1e6 * n / totals[y] for y, n in counts.items() if totals.get(y)}

    pre = [r for y, r in rates.items() if origin_year - PRE_WINDOW <= y < origin_year]
    post = [r for y, r in rates.items() if y > origin_year]
    base = mean(pre) if pre else 0.0
    post_rate = mean(post) if post else 0.0
    lift = (post_rate / base) if base > 0 else float("inf")

    if base == 0:
        verdict = "clean"
    elif lift >= CLEAN:
        verdict = "clean"
    elif lift >= SUSPECT:
        verdict = "ok"
    else:
        verdict = "polysemy risk"

    return {
        "pre_origin_hits": sum(n for y, n in counts.items() if y < origin_year),
        "baseline_per_M": round(base, 3),
        "post_per_M": round(post_rate, 3),
        "lift": None if lift == float("inf") else round(lift, 1),
        "verdict": verdict,
        "usable": verdict != "polysemy risk",
    }


def screen_all(concepts, totals=None):
    totals = totals or openalex.total_counts()
    out = {}
    for c in concepts:
        if c.science_origin is None:
            continue
        out[c.name] = screen(c.terms, c.science_origin, totals=totals)
    return out
