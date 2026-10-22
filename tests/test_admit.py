"""The screen must be matched to the detector it protects.

These tests encode the failure described in white paper 3. The share-based
polysemy screen passes genetic algorithms; a count-based detector is destroyed
by the same 140 mis-dated documents. If someone later tightens the detector
without rerunning admissibility, these fail.
"""
import pytest

from sahar import admit, openalex, polysemy, threshold


@pytest.fixture(scope="module")
def totals():
    return openalex.total_counts()


@pytest.fixture(scope="module")
def data(totals):
    d, _ = threshold.load(totals=totals)
    return d


def test_share_screen_passes_genetic_algorithms(data, totals):
    """The premise of the failure: the old screen sees nothing wrong."""
    import sahar.concepts as concepts
    ga = {c.name: c for c in concepts.CONTROLS}["genetic algorithms"]
    assert polysemy.screen(ga.terms, ga.science_origin,
                           totals=totals)["verdict"] != "polysemy risk"


def test_genetic_algorithms_carries_predated_records(data):
    """140 documents before 1975, which is the thing the share screen divides away."""
    counts, origin = data["genetic algorithms"]
    pre = sum(n for y, n in counts.items() if y < origin)
    assert pre > 100, f"expected a large pre-origin count, got {pre}"


def test_admissibility_rejects_it_for_a_count_detector(data, totals):
    counts, origin = data["genetic algorithms"]
    assert not admit.admissible(counts, totals, origin, c_ref=3, beta=0.0)


def test_admissibility_accepts_the_clean_controls(data, totals):
    for name in ("information theory", "computer graphics", "fractal"):
        counts, origin = data[name]
        assert admit.admissible(counts, totals, origin, c_ref=3, beta=0.0), name


def test_screen_verdict_depends_on_the_detector(data, totals):
    """The central claim: a concept valid for one detector is invalid for another."""
    counts, origin = data["genetic algorithms"]
    loose = admit.admissible(counts, totals, origin, c_ref=20, beta=1.0)
    tight = admit.admissible(counts, totals, origin, c_ref=3, beta=0.0)
    assert loose and not tight, "the screen must be detector dependent"


def test_guarded_fit_beats_the_four_year_target(data, totals):
    from statistics import mean
    clean = {k: v for k, v in data.items() if k != "genetic algorithms"}
    errs = []
    for name, (counts, doc) in clean.items():
        m = threshold.onset(counts, totals, 2, 0.0)
        errs.append(abs(m - doc))
    assert mean(errs) <= 4.0, f"guarded MAE regressed to {mean(errs):.1f}"
