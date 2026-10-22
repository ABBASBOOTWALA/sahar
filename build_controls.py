"""Screen the expanded candidate set and report how many become calibration points.

Candidates are deliberately over-inclusive. The screens decide which survive:

  1. the polysemy screen, for terms carrying an older unrelated sense
  2. the admissibility screen, for records mis-dated before the origin
  3. detection itself, which some concepts are simply too small to trigger

    python build_controls.py
"""
import json
import math
from pathlib import Path
from statistics import mean

from sahar import admit, concepts, controls_v2, openalex, polysemy, resolve, threshold

C_REF, BETA = 2, 0.0
OUT = Path("data/controls_v2_screened.json")


def main():
    totals = openalex.total_counts()
    strat = resolve.PhraseField()
    rows = []

    pool = controls_v2.UNCONTESTED + [c for c in concepts.CONTROLS]
    for c in pool:
        counts = strat.counts(c)
        total = sum(counts.values())
        pre = sum(n for y, n in counts.items() if y < c.science_origin)
        poly = polysemy.screen(c.terms, c.science_origin, totals=totals)["verdict"]
        fires = admit.fires_before_origin(counts, totals, c.science_origin, C_REF, BETA)
        onset = threshold.onset(counts, totals, C_REF, BETA)
        err = None if onset is None else onset - c.science_origin
        usable = (poly != "polysemy risk") and (fires is None) and (onset is not None)
        rows.append(dict(name=c.name, origin=c.science_origin, total=total, pre=pre,
                         polysemy=poly, fires=fires, onset=onset, err=err,
                         usable=usable))

    rows.sort(key=lambda r: -r["total"])
    print(f"{'concept':<32}{'orig':>6}{'docs':>9}{'pre':>6}{'poly':>8}"
          f"{'fires':>7}{'onset':>7}{'err':>6}  use")
    print("-" * 94)
    for r in rows:
        e = "" if r["err"] is None else format(r["err"], "+d")
        poly = "FLAG" if r["polysemy"] == "polysemy risk" else "ok"
        print(f"{r['name'][:30]:<32}{r['origin']:>6}{r['total']:>9}{r['pre']:>6}"
              f"{poly:>8}{str(r['fires'] or '-'):>7}{str(r['onset'] or '-'):>7}"
              f"{e:>6}  {'YES' if r['usable'] else ''}")

    usable = [r for r in rows if r["usable"]]
    print()
    print(f"candidates screened         : {len(rows)}")
    print(f"  rejected by polysemy      : {sum(1 for r in rows if r['polysemy'] == 'polysemy risk')}")
    print(f"  rejected by admissibility : {sum(1 for r in rows if r['fires'] is not None)}")
    print(f"  never detected            : {sum(1 for r in rows if r['onset'] is None)}")
    print(f"  USABLE CALIBRATION POINTS : {len(usable)}   (was 3)")

    if usable:
        errs = [r["err"] for r in usable]
        print()
        print(f"signed error: mean {mean(errs):+.1f}  "
              f"range {min(errs):+d} to {max(errs):+d}")
        print(f"  late {sum(1 for e in errs if e > 0)}, "
              f"on time {sum(1 for e in errs if e == 0)}, "
              f"early {sum(1 for e in errs if e < 0)}")
        vols = [math.log10(r["total"]) for r in usable]
        print(f"volume span: {min(10**v for v in vols):,.0f} to "
              f"{max(10**v for v in vols):,.0f} documents")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=1))
    print(f"\nwritten to {OUT}")


if __name__ == "__main__":
    main()
