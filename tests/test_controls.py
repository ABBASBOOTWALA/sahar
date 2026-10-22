"""Regression tests: the documented controls must keep behaving.

These encode the gate. If disambiguation degrades, or the polysemy screen stops
catching holography, CI fails rather than a person noticing months later.
"""
import pytest

from sahar import concepts, onset, openalex, polysemy, resolve

BEST = "phrase+field"


@pytest.fixture(scope="session")
def totals():
    return openalex.total_counts()


def test_polysemy_screen_flags_known_collisions(totals):
    """holography collides with probate law; artificial life with vitalism."""
    for name in ("holography", "artificial life"):
        c = concepts.by_name(name)
        assert polysemy.screen(c.terms, c.science_origin, totals=totals)["verdict"] \
            == "polysemy risk", f"{name} should be flagged"


def test_polysemy_screen_passes_clean_concepts(totals):
    for name in ("information theory", "computer graphics", "fractal"):
        c = concepts.by_name(name)
        assert polysemy.screen(c.terms, c.science_origin, totals=totals)["usable"], \
            f"{name} should pass"


def test_controls_have_documented_origins():
    for c in concepts.CONTROLS:
        assert c.science_origin is not None
        assert c.origin_note, f"{c.name} needs a citable origin note"


def test_onset_floor_is_reported_as_censored():
    assert onset.is_censored(1900)
    assert not onset.is_censored(1948)


def test_relation_respects_tolerance():
    assert onset.relation(1980, 1981).startswith("simultaneous")
    assert onset.relation(1990, 1960).startswith("science-first")
    assert onset.relation(1960, 1990).startswith("art-first")
    assert onset.relation(1977, None) == "art-only"
