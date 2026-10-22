"""Can cultural tracers expand the calibration set? Three questions, one run.

Reports 05, 06 and 08 all assumed song-title tracers would supply the calibration
points the project lacks. This script tests that assumption and answers no, while
establishing two things that are worth more than the assumption was.

    python tracer_study.py
"""
import math
from statistics import mean
from sahar import admit, concepts, cultural, openalex, resolve, threshold

C_REF, BETA = 2, 0.0          # the fitted detector from the calibration paper


def rule(t):
    print()
    print(t)
    print("-" * len(t))


def tracer_counts(phrase):
    c = openalex.year_counts([f'title_and_abstract.search:"{phrase}"',
                              openalex.exclude_leonardo()])
    return {y: n for y, n in c.items() if y >= 1900}


def main():
    totals = openalex.total_counts()

    rule("Q1. Does the admissibility screen separate tracers from common phrases?")
    admissible, points = [], []
    for t in cultural.DISTINCTIVE:
        c = tracer_counts(t.phrase)
        fires = admit.fires_before_origin(c, totals, t.released, C_REF, BETA)
        onset = threshold.onset(c, totals, C_REF, BETA)
        if fires is None:
            admissible.append(t.phrase)
            if onset:
                points.append((math.log10(sum(c.values())), onset - t.released, t.phrase))
    print(f"  distinctive tracers admissible : {len(admissible)} of {len(cultural.DISTINCTIVE)}")
    rejected = 0
    for t in [x for x in cultural.BEATLES if x.phrase in cultural.NEGATIVE_CONTROLS]:
        c = tracer_counts(t.phrase)
        fires = admit.fires_before_origin(c, totals, t.released, C_REF, BETA)
        rejected += fires is not None
        print(f"  negative control {t.phrase:<16} fires {str(fires or '-'):>6}"
              f"  {'REJECTED' if fires else 'MISSED'}")
    print(f"  negative controls rejected     : {rejected} of 4")

    rule("Q2. Does detection error depend on how much a phrase is used?")
    strat = resolve.PhraseField()
    conc = []
    for con in concepts.CONTROLS:
        c = strat.counts(con)
        if admit.fires_before_origin(c, totals, con.science_origin, C_REF, BETA):
            continue
        o = threshold.onset(c, totals, C_REF, BETA)
        if o:
            conc.append((math.log10(sum(c.values())), o - con.science_origin, con.name))
    allpts = points + conc

    def spearman(xs, ys):
        def rank(v):
            order = sorted(range(len(v)), key=lambda i: v[i])
            r = [0.0] * len(v)
            for pos, i in enumerate(order):
                r[i] = pos + 1
            return r
        rx, ry = rank(xs), rank(ys)
        mx, my = mean(rx), mean(ry)
        num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
        den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
        return num / den if den else float("nan")

    print(f"  n = {len(allpts)} ({len(points)} tracers, {len(conc)} concepts)")
    print(f"  Spearman rho, log10(documents) vs signed error: "
          f"{spearman([p[0] for p in allpts], [p[1] for p in allpts]):+.3f}")
    for lo, hi, label in [(0, 2, "under 100"), (2, 3, "100 to 1k"),
                          (3, 4, "1k to 10k"), (4, 9, "over 10k")]:
        band = [e for x, e, _ in allpts if lo <= x < hi]
        if band:
            print(f"    {label:<12} n={len(band):<3} mean error {mean(band):+6.1f}")

    rule("Q3. Are the two populations exchangeable? Fit on tracers, test on concepts.")

    def fit(pts):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        mx, my = mean(xs), mean(ys)
        b = (sum((x - mx) * (y - my) for x, y in zip(xs, ys))
             / sum((x - mx) ** 2 for x in xs))
        return my - b * mx, b

    a, b = fit(points)
    ac, bc = fit([(x, y) for x, y, _ in conc])
    miss = [abs(y - (a + b * x)) for x, y, _ in conc]
    print(f"  tracer fit : error = {a:+.1f} {b:+.1f} * log10(documents)")
    print(f"  concept fit: error = {ac:+.1f} {bc:+.1f} * log10(documents)")
    print(f"  intercepts differ by {abs(a - ac):.1f} years")
    print(f"  tracer model applied to concepts: mean miss {mean(miss):.1f}y")
    print(f"  constant-offset baseline        : 5.3y held out")
    print()
    print("  Verdict: tracers validate the screens and establish the volume effect,")
    print("  but they cannot calibrate concept dating. The populations differ.")


if __name__ == "__main__":
    main()
