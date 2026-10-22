"""Score disambiguation strategies against documented science origins.

This turns "does topic filtering work?" from an argument into a number. Each
strategy measures a science-side onset for every control concept; the error is
the distance from the documented origin year, and the strategy's score is the
mean absolute error across controls.

A strategy that cannot recover Gabor 1948 for holography is not one we can trust
on a concept whose history we do not already know.
"""
import json
from pathlib import Path
from statistics import median

from . import concepts, config, onset, openalex, resolve

OUT = Path(__file__).resolve().parent.parent / "data"


def evaluate(strategies=None, controls=None, verbose=True):
    strategies = strategies or resolve.ALL
    controls = controls or concepts.CONTROLS
    totals = openalex.total_counts()

    results = {}
    for s in strategies:
        rows, errors = [], []
        for c in controls:
            measured = onset.science_onset_for(c, s, totals)
            err = None if measured is None else abs(measured - c.science_origin)
            if err is not None:
                errors.append(err)
            rows.append({
                "concept": c.name,
                "documented": c.science_origin,
                "measured": measured,
                "error": err,
                "censored": onset.is_censored(measured),
            })
        results[s.name] = {
            "description": s.description,
            "rows": rows,
            "mae": round(sum(errors) / len(errors), 1) if errors else None,
            "median_error": median(errors) if errors else None,
            "within_5y": sum(1 for e in errors if e <= 5),
            "censored": sum(1 for r in rows if r["censored"]),
            "missing": sum(1 for r in rows if r["measured"] is None),
        }
        if verbose:
            _print_strategy(s, results[s.name], controls)

    OUT.mkdir(exist_ok=True)
    (OUT / "strategy_scores.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
    return results


def _print_strategy(s, res, controls):
    print(f"\n### {s.name}  —  {s.description}")
    print(f"{'concept':22}{'documented':>12}{'measured':>10}{'error':>8}")
    print("-" * 54)
    for r in res["rows"]:
        m = "none" if r["measured"] is None else str(r["measured"])
        if r["censored"]:
            m += "*"
        e = "-" if r["error"] is None else f"{r['error']:>4}y"
        print(f"{r['concept'][:21]:22}{r['documented']:>12}{m:>10}{e:>8}")
    print(f"{'':22}{'':>12}{'MAE':>10}{res['mae']:>7}y"
          f"   within 5y: {res['within_5y']}/{len(controls)}"
          f"   censored: {res['censored']}")


def summary(results):
    print("\n" + "=" * 62)
    print(f"{'strategy':28}{'MAE':>8}{'median':>9}{'within 5y':>11}{'censored':>10}")
    print("-" * 62)
    ranked = sorted(results.items(), key=lambda kv: (kv[1]["mae"] is None, kv[1]["mae"]))
    for name, r in ranked:
        mae = "-" if r["mae"] is None else f"{r['mae']:.1f}"
        med = "-" if r["median_error"] is None else f"{r['median_error']:.0f}"
        print(f"{name:28}{mae:>8}{med:>9}{r['within_5y']:>11}{r['censored']:>10}")
    best = ranked[0]
    print("-" * 62)
    print(f"best: {best[0]}  (MAE {best[1]['mae']}y)")
    print("* = onset sits on the 1900 guard year and is censored, not measured.")
    return ranked[0][0]


if __name__ == "__main__":
    summary(evaluate())
