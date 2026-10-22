"""A threshold that scales with corpus size.

Two earlier designs failed in opposite directions.

  v1, a fixed document count, fired on the earliest metadata error anywhere in
  324 million records.

  v3, a fixed share of annual output, is harder to clear as the corpus grows. In
  1948 a handful of papers was a large share of a small literature; by 1975 the
  same concept needs far more papers to reach the same share. This is the
  likeliest cause of the systematic late bias measured in bias.py, where every
  clean control reads late and the two 1975 origins read latest of all.

This module interpolates between them with a single exponent.

    required_count(y) = C_ref * (T_y / T_ref) ** beta

where T_y is total output in year y and T_ref is output in a reference year.

    beta = 1  ->  fixed share, the v3 behaviour
    beta = 0  ->  fixed count, the v1 behaviour

Fitting beta therefore does more than tune a number. Its value is a measurement
of how much corpus growth actually matters, and it tells us which of the two
earlier designs was closer to right.

Both parameters are fit by leave-one-out so that no control is scored against a
threshold fitted on itself.
"""
from statistics import mean

from . import concepts, openalex, polysemy, resolve

REF_YEAR = 1975
MIN_YEAR = 1900
SUSTAIN = 3


def onset(counts, totals, c_ref, beta, ref_year=REF_YEAR, sustain=SUSTAIN):
    """First year clearing a size-scaled count that then holds."""
    t_ref = totals.get(ref_year)
    if not t_ref:
        return None
    years = sorted(y for y in counts if y >= MIN_YEAR and totals.get(y))
    if not years:
        return None

    def clears(y):
        t = totals.get(y)
        if not t:
            return False
        need = c_ref * (t / t_ref) ** beta
        return counts.get(y, 0) >= need

    for y in years:
        if all(clears(y + i) for i in range(sustain)):
            return y
    return None


def _control_counts(strategy, totals, screen=True):
    """Year counts and documented origin for each control passing the screen."""
    out = {}
    for c in concepts.CONTROLS:
        if screen:
            s = polysemy.screen(c.terms, c.science_origin, totals=totals)
            if s["verdict"] == "polysemy risk":
                continue
        out[c.name] = (strategy.counts(c), c.science_origin)
    return out


def _mae(data, totals, c_ref, beta, exclude=None):
    errs = []
    for name, (counts, documented) in data.items():
        if name == exclude:
            continue
        m = onset(counts, totals, c_ref, beta)
        if m is None:
            errs.append(60.0)          # a miss is penalised, not silently dropped
        else:
            errs.append(abs(m - documented))
    return mean(errs) if errs else float("inf")


def fit(data, totals, c_grid=None, beta_grid=None, exclude=None):
    c_grid = c_grid or [2, 3, 5, 8, 12, 20, 30, 50, 80, 120]
    beta_grid = beta_grid or [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    best = (float("inf"), None, None)
    for c in c_grid:
        for b in beta_grid:
            e = _mae(data, totals, c, b, exclude=exclude)
            if e < best[0]:
                best = (e, c, b)
    return {"mae": best[0], "c_ref": best[1], "beta": best[2]}


def leave_one_out(data, totals):
    """Fit on all controls but one, score on the held-out control."""
    rows = []
    for name, (counts, documented) in data.items():
        f = fit(data, totals, exclude=name)
        m = onset(counts, totals, f["c_ref"], f["beta"])
        rows.append({
            "concept": name, "documented": documented, "measured": m,
            "c_ref": f["c_ref"], "beta": f["beta"],
            "error": None if m is None else abs(m - documented),
        })
    scored = [r["error"] for r in rows if r["error"] is not None]
    return rows, (mean(scored) if scored else None)


def load(strategy=None, totals=None):
    strategy = strategy or resolve.PhraseField()
    totals = totals or openalex.total_counts()
    return _control_counts(strategy, totals), totals
