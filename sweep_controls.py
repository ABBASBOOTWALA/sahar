"""Coverage against accuracy, across detector settings.

Kashf section 8.3 warned that a strict detector may score well partly because
the admissibility screen removes the cases that would expose it. With four
candidates that could not be tested. With 43 it can.

For each setting we report how many candidates survive screening and the error
on those that do. A setting that admits few points and scores well has not
necessarily earned it.

    python sweep_controls.py
"""
import math
from statistics import mean

from sahar import admit, concepts, controls_v2, openalex, polysemy, resolve, threshold


def main():
    totals = openalex.total_counts()
    strat = resolve.PhraseField()
    pool = controls_v2.UNCONTESTED + list(concepts.CONTROLS)

    cache = {}
    for c in pool:
        verdict = polysemy.screen(c.terms, c.science_origin, totals=totals)["verdict"]
        if verdict == "polysemy risk":
            continue
        cache[c.name] = (strat.counts(c), c.science_origin)
    print(f"candidates passing the polysemy screen: {len(cache)} of {len(pool)}")
    print()

    print(f"{'C':>4}{'beta':>6}{'admitted':>10}{'MAE':>8}{'mean':>8}{'late':>6}{'early':>7}")
    print("-" * 49)
    best = None
    for c_ref in (2, 3, 5, 8, 12, 20, 40, 80):
        for beta in (0.0, 0.5, 1.0):
            errs = []
            for counts, origin in cache.values():
                if admit.fires_before_origin(counts, totals, origin, c_ref, beta):
                    continue
                o = threshold.onset(counts, totals, c_ref, beta)
                if o is not None:
                    errs.append(o - origin)
            if not errs:
                continue
            mae = mean(abs(e) for e in errs)
            row = (c_ref, beta, len(errs), mae, mean(errs),
                   sum(1 for e in errs if e > 0), sum(1 for e in errs if e < 0))
            print(f"{c_ref:>4}{beta:>6.1f}{len(errs):>10}{mae:>8.1f}"
                  f"{mean(errs):>+8.1f}{row[5]:>6}{row[6]:>7}")
            # prefer the setting admitting the most points, breaking ties on MAE
            if best is None or (len(errs), -mae) > (best[2], -best[3]):
                best = row

    print()
    print(f"most points admitted: C={best[0]}, beta={best[1]} -> "
          f"{best[2]} points at MAE {best[3]:.1f}")
    print()
    print("Read down the admitted column. If accuracy improves only as coverage")
    print("falls, the strict settings are being flattered by their own screen.")


if __name__ == "__main__":
    main()
