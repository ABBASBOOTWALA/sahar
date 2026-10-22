"""Can the late bias now be corrected? Leave-one-out on the expanded set.

Kashf could not fit a correction: three points cannot identify a parameter, and
the exponent it introduced scaled with the wrong quantity, corpus growth by year
rather than the concept's own literature size. tracer_study.py found the latter
correlates with error at rho = -0.884.

This tests three correction models honestly, each scored by leave-one-out so no
concept is corrected using a model fitted to itself.

    python fit_correction.py
"""
import math
from statistics import mean

from sahar import admit, concepts, controls_v2, openalex, polysemy, resolve, threshold

SETTINGS = [(5, 0.0), (12, 0.0), (20, 0.0)]


def collect(c_ref, beta, totals, strat, pool):
    pts = []
    for c in pool:
        if polysemy.screen(c.terms, c.science_origin,
                           totals=totals)["verdict"] == "polysemy risk":
            continue
        counts = strat.counts(c)
        if admit.fires_before_origin(counts, totals, c.science_origin, c_ref, beta):
            continue
        o = threshold.onset(counts, totals, c_ref, beta)
        if o is None:
            continue
        pts.append((math.log10(max(sum(counts.values()), 1)), o - c.science_origin, c.name))
    return pts


def linfit(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    mx, my = mean(xs), mean(ys)
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return my, 0.0
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    return my - b * mx, b


def loo(pts, model):
    out = []
    for i, (x, y, _) in enumerate(pts):
        others = pts[:i] + pts[i + 1:]
        out.append(abs(y - model(others, x)))
    return mean(out)


def main():
    totals = openalex.total_counts()
    strat = resolve.PhraseField()
    pool = controls_v2.UNCONTESTED + list(concepts.CONTROLS)

    print(f"{'setting':<14}{'n':>4}{'raw':>8}{'offset':>9}{'volume':>9}{'winner':>10}")
    print("-" * 56)
    for c_ref, beta in SETTINGS:
        pts = collect(c_ref, beta, totals, strat, pool)
        if len(pts) < 6:
            continue
        raw = mean(abs(y) for _, y, _ in pts)
        off = loo(pts, lambda o, x: mean(p[1] for p in o))
        vol = loo(pts, lambda o, x: (lambda ab: ab[0] + ab[1] * x)(linfit(o)))
        win = "volume" if vol < off else "offset"
        print(f"C={c_ref}, beta={beta:<5}{len(pts):>4}{raw:>8.1f}"
              f"{off:>9.1f}{vol:>9.1f}{win:>10}")

    c_ref, beta = 12, 0.0
    pts = collect(c_ref, beta, totals, strat, pool)
    a, b = linfit(pts)
    print()
    print(f"Fitted on all {len(pts)} points at C={c_ref}, beta={beta}:")
    print(f"  error = {a:+.1f} {b:+.1f} * log10(documents)")
    print(f"  a concept with 1,000 documents reads {a + b * 3:+.1f} years late")
    print(f"  a concept with 1,000,000 documents reads {a + b * 6:+.1f} years late")
    print()
    print("Kashf baseline, for comparison: 3 points, 8.0 raw, 5.3 corrected by offset.")


if __name__ == "__main__":
    main()
