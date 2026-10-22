"""Regenerate every table in white paper 3, in the order they appear.

    python reproduce_paper3.py

Everything comes from the OpenAlex request cache, so a second run is offline
and identical. A cached run is a reproducible run.
"""
from statistics import mean

from sahar import admit, bias, concepts, openalex, polysemy, resolve, threshold

GA = "genetic algorithms"
BETAS = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]        # printed
CS = [2, 3, 5, 8, 12, 20]                     # printed
FINE_BETAS = [round(i * 0.1, 1) for i in range(11)]   # searched
FINE_CS = [2, 3, 5, 8, 12, 20, 30, 50]                # searched


def rule(title):
    print()
    print(title)
    print("-" * len(title))


def main():
    totals = openalex.total_counts()
    data, _ = threshold.load(totals=totals)
    errs = bias.signed_errors(totals=totals)

    rule("Section 1: the error is systematic")
    for n, e in errs.items():
        print(f"  {n:<22}{e['documented']}  ->  {e['measured']}   {e['signed_error']:+d}")
    raw_mae = mean(abs(e["signed_error"]) for e in errs.values())
    print(f"  mean absolute error: {raw_mae:.1f}   mean signed: {bias.estimate(errs):+.1f}")

    rule("Section 2: corpus growth")
    for y in (1948, 1963, 1975, 1990, 2024):
        print(f"  {y}  {totals[y]:>12,}")
    print(f"  1948 to 2024: {totals[2024] / totals[1948]:.1f}x")

    rule("Section 3: constant offset, leave one out")
    rows, raw, corr = bias.leave_one_out(errs)
    for r in rows:
        print(f"  {r['concept']:<22}corrected {r['corrected']:>7}   error {r['error_after']}")
    print(f"  MAE {raw:.1f} -> {corr:.1f}")

    rule("Section 4: scale aware threshold, unguarded")
    full = threshold.fit(data, totals)
    print(f"  fitted on all four: C={full['c_ref']} beta={full['beta']} MAE={full['mae']:.1f}")
    trows, tmae = threshold.leave_one_out(data, totals)
    for r in trows:
        print(f"  {r['concept']:<22}{r['documented']}  ->  {r['measured']}   error {r['error']}")
    print(f"  held out MAE: {tmae:.1f}")

    rule("Section 5: what the share screen sees")
    strat = resolve.PhraseField()
    print(f"  {'concept':<22}{'origin':>7}{'pre':>6}{'total':>10}{'share':>9}  screen")
    for c in concepts.CONTROLS:
        counts = strat.counts(c)
        pre = sum(n for y, n in counts.items() if y < c.science_origin)
        allc = sum(counts.values())
        v = polysemy.screen(c.terms, c.science_origin, totals=totals)["verdict"]
        print(f"  {c.name:<22}{c.science_origin:>7}{pre:>6}{allc:>10,}"
              f"{pre / allc * 100:>8.3f}%  {v}")

    rule("Section 5: admissibility depends on the detector")
    for c_ref, beta, label in [(20, 1.0, "loose, our standing method"),
                               (3, 1.0, "tighter, still share based"),
                               (3, 0.0, "the fitted setting, count based")]:
        verdicts = []
        for r in admit.audit(data, totals, c_ref, beta):
            verdicts.append(f"{r['concept'].split()[0]}="
                            f"{'ok' if r['admissible'] else r['false_onset']}")
        print(f"  C={c_ref:<3}beta={beta}  {label}")
        print(f"      {'  '.join(verdicts)}")

    rule("Section 6: comparison on the three admissible controls")
    clean = {k: v for k, v in data.items() if k != GA}
    clean_errs = {k: v for k, v in errs.items() if k != GA}
    base = mean(abs(e["signed_error"]) for e in clean_errs.values())
    _, _, off_out = bias.leave_one_out(clean_errs)
    off_in = mean(abs((e["measured"] - bias.estimate(clean_errs)) - e["documented"])
                  for e in clean_errs.values())
    thr = mean(abs(threshold.onset(ct, totals, 2, 0.0) - dc) for ct, dc in clean.values())
    print(f"  {'model':<30}{'params':>7}{'in':>8}{'out':>8}{'gap':>7}")
    for name, p, i, o in [("no correction", 0, base, base),
                          ("constant offset", 1, off_in, off_out),
                          ("scale aware, guarded", 2, thr, thr)]:
        print(f"  {name:<30}{p:>7}{i:>7.1f}y{o:>7.1f}y{o - i:>+7.1f}")

    rule("Section 7: beta is not identified")
    print("  C  " + "".join(f"{b:>7.1f}" for b in BETAS))
    def err(c, b):
        """None if the setting is invalid for any control; a miss is penalised."""
        vals = []
        for ct, dc in clean.values():
            if not admit.admissible(ct, totals, dc, c, b):
                return None
            m = threshold.onset(ct, totals, c, b)
            vals.append(60.0 if m is None else abs(m - dc))
        return mean(vals)

    for c in CS:
        cells = []
        for b in BETAS:
            v = err(c, b)
            cells.append("    n/a" if v is None else f"{v:>7.1f}")
        print(f"  {c:<3}" + "".join(cells))

    grid = [(c, b, err(c, b)) for c in FINE_CS for b in FINE_BETAS]
    grid = [g for g in grid if g[2] is not None]
    best = min(v for _, _, v in grid)
    near = [(c, b) for c, b, v in grid if v <= best + 1.0]
    print(f"  best {best:.1f} over {len(grid)} valid settings "
          f"({len(FINE_CS) * len(FINE_BETAS)} searched)")
    print(f"  within 1 year of best: {len(near)}")
    print(f"    beta spans {min(b for _, b in near)} to {max(b for _, b in near)}")
    print(f"    C spans    {min(c for c, _ in near)} to {max(c for c, _ in near)}")

    rule("Section 6: strict settings admit fewer controls")
    for c in CS:
        n = sum(1 for nm, (ct, dc) in data.items()
                if admit.admissible(ct, totals, dc, c, 0.0))
        print(f"  C={c:<4}admissible: {n} of {len(data)}")


if __name__ == "__main__":
    main()
