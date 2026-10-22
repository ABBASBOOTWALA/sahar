"""Concept registry, with independently documented science-side origins.

The origins below are the ground truth against which disambiguation strategies
are scored. Each is a dated, checkable event in the history of the field,
established outside this corpus. They are not derived from any measurement made
here, which is what makes them usable as a test.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Concept:
    name: str
    terms: tuple
    science_origin: int | None      # documented origin year, None if not applicable
    origin_note: str
    expect: str                     # pre-registered expectation
    is_control: bool = False


CONTROLS = [
    Concept("holography", ("holography", "holographic", "hologram"), 1948,
            "Gabor, 'A new microscopic principle', Nature 1948. Nobel 1971.",
            "science-first", True),
    Concept("information theory", ("information theory", "information-theoretic"), 1948,
            "Shannon, 'A mathematical theory of communication', 1948.",
            "science-first", True),
    Concept("computer graphics", ("computer graphics", "computer-generated"), 1963,
            "Sutherland's Sketchpad, MIT 1963.",
            "science-first", True),
    Concept("fractal", ("fractal", "fractals", "fractal geometry"), 1975,
            "Mandelbrot, 'Les objets fractals', 1975.",
            "science-first", True),
    Concept("artificial life", ("artificial life", "a-life"), 1986,
            "Langton coins the term; first workshop 1987.",
            "science-first", True),
    Concept("genetic algorithms", ("genetic algorithm", "genetic algorithms"), 1975,
            "Holland, 'Adaptation in Natural and Artificial Systems', 1975.",
            "science-first", True),
]

# Not controls: no independently documented science origin, so they cannot score
# a strategy. Carried because they are what the study is actually about.
TEST_SET = [
    Concept("visual perception", ("visual perception",), None,
            "Perception psychology long predates the corpus; no single origin date.",
            "science-first"),
    Concept("kinetic art", ("kinetic art",), None,
            "Gabo and Pevsner, 1920s. 'kinetic' alone collides with kinetic theory.",
            "art-first"),
    Concept("sound sculpture", ("sound sculpture", "sound art"), None,
            "Art-origin term with no prior science counterpart.",
            "art-first"),
    Concept("telepresence", ("telepresence",), None,
            "Minsky 1980 against Kac's telepresence art; genuinely contested.",
            "ambiguous"),
]

ALL = CONTROLS + TEST_SET


def by_name(name):
    for c in ALL:
        if c.name == name:
            return c
    raise KeyError(name)
