"""Measure how long a dated cultural phrase takes to enter scientific language.

The method exploits a property the science concepts do not have: a phrase with a
known release date supplies its own null model. Occurrences before release cannot
be references, so the pre-release period measures the false-positive rate
directly.

For each tracer we compute

  base   = mean rate per million documents in the years BEFORE release
  post   = mean rate per million documents in the years AFTER release
  lift   = post / base, the signal-to-noise ratio of the phrase
  onset  = first year where the rate exceeds the pre-release baseline and holds
  latency = onset - release

A phrase whose lift is near 1 carries no signal and should be discarded. That
rejection is automatic and statistical, requiring no language model, which makes
it a cheap complement to the LLM screening used by Budel et al. (2026).
"""
from statistics import mean

from . import openalex

PRE_WINDOW = 20      # years before release used for the baseline
SUSTAIN = 3          # years the signal must hold
LIFT_FLOOR = 3.0     # below this the phrase is treated as carrying no signal


def _rates(phrase, totals):
    counts = openalex.year_counts([f'title.search:"{phrase}"'])
    return {y: 1e6 * n / totals[y] for y, n in counts.items() if totals.get(y)}, counts


def measure(tracer, totals):
    rates, counts = _rates(tracer.phrase, totals)
    if not rates:
        return None

    pre = [r for y, r in rates.items()
           if tracer.released - PRE_WINDOW <= y < tracer.released]
    post = [r for y, r in rates.items() if y > tracer.released]

    base = mean(pre) if pre else 0.0
    post_rate = mean(post) if post else 0.0
    lift = (post_rate / base) if base > 0 else (float("inf") if post_rate > 0 else 0.0)

    # onset: first year after release where the rate clears the baseline and holds
    threshold = max(base * 2, 1e-9)
    onset = None
    years = sorted(y for y in rates if y >= tracer.released)
    for y in years:
        if all(rates.get(y + i, 0) > threshold for i in range(SUSTAIN)):
            onset = y
            break

    return {
        "phrase": tracer.phrase,
        "released": tracer.released,
        "note": tracer.note,
        "total_hits": sum(counts.values()),
        "pre_hits": sum(n for y, n in counts.items() if y < tracer.released),
        "baseline_per_M": round(base, 4),
        "post_per_M": round(post_rate, 4),
        "lift": None if lift == float("inf") else round(lift, 1),
        "clean": bool(base == 0),
        "onset": onset,
        "latency": None if onset is None else onset - tracer.released,
    }


def run(tracers, totals=None):
    totals = totals or openalex.total_counts()
    out = []
    for t in tracers:
        m = measure(t, totals)
        if m:
            out.append(m)
    return out


def report(rows):
    print(f"{'phrase':38}{'rel':>5}{'hits':>7}{'pre':>5}{'lift':>8}{'onset':>7}{'lat':>5}")
    print("-" * 78)
    for r in sorted(rows, key=lambda r: (r["lift"] is not None, -(r["lift"] or 0))):
        lift = "clean" if r["clean"] else f"{r['lift']:.1f}"
        onset = r["onset"] or "-"
        lat = "-" if r["latency"] is None else f"{r['latency']:+d}"
        flag = " <-" if "NEGATIVE" in r["note"] else ""
        print(f"{r['phrase'][:37]:38}{r['released']:>5}{r['total_hits']:>7}"
              f"{r['pre_hits']:>5}{lift:>8}{str(onset):>7}{lat:>5}{flag}")

    lat = [r["latency"] for r in rows if r["latency"] is not None
           and "NEGATIVE" not in r["note"]]
    if lat:
        print("-" * 78)
        print(f"distinctive tracers with a measurable onset: {len(lat)}")
        print(f"median diffusion latency: {sorted(lat)[len(lat)//2]} years")
        print(f"range: {min(lat)} to {max(lat)} years")
