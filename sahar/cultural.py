"""Cultural tracers: phrases with known, dated origins.

Why these matter for a project about conceptual precedence.

Every scientific concept we have tried to date suffers from polysemy. Holography
collides with handwritten wills, kinetic with the kinetic theory of gases,
artificial life with vitalism. Each collision hands the science side a false early
onset, and that mechanism explains most of the bias found in the pilot.

A song title has no prior technical sense and an exact release date. So this set
provides what the science controls cannot:

  1. Exact ground truth. Sgt. Pepper was released on 1 June 1967. Gabor 1948 is a
     defensible scholarly choice among several.
  2. Large n. Thousands of matching documents rather than six.
  3. A free null model. Any occurrence before the release date is, by
     construction, not a reference. The pre-release period measures the
     false-positive rate directly, with no model and no judgement.

Property 3 is the useful one. It gives a statistical alternative to the LLM
screening used by Budel, Kooij and Tjepkema (PLOS ONE, 2026) for separating
deliberate wordplay from coincidental phrasing.

DATES: years are from the original UK release. They are transcribed from general
knowledge and should be verified against a discography before publication.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Tracer:
    phrase: str
    released: int
    note: str = ""


# Ordered roughly by how unlikely the phrase is to occur by chance. The ordinary
# English ones are kept deliberately: they are the negative controls, and the
# method should reject them.
BEATLES = [
    # Distinctive: essentially impossible before 1962
    Tracer("lucy in the sky with diamonds", 1967, "Sgt. Pepper"),
    Tracer("strawberry fields forever", 1967, "single, February"),
    Tracer("sgt. pepper's lonely hearts club band", 1967),
    Tracer("a hard day's night", 1964),
    Tracer("eleanor rigby", 1966, "Revolver"),
    Tracer("norwegian wood", 1965, "Rubber Soul"),
    Tracer("yellow submarine", 1966, "Revolver"),
    Tracer("tomorrow never knows", 1966, "Revolver"),
    Tracer("magical mystery tour", 1967),
    Tracer("back in the ussr", 1968, "White Album"),
    Tracer("while my guitar gently weeps", 1968, "White Album"),
    Tracer("ob-la-di, ob-la-da", 1968, "White Album"),
    Tracer("hey jude", 1968, "single"),
    Tracer("paperback writer", 1966, "single"),
    Tracer("ticket to ride", 1965, "single"),
    Tracer("i want to hold your hand", 1963, "single"),

    # Moderately distinctive
    Tracer("the long and winding road", 1970, "Let It Be"),
    Tracer("with a little help from my friends", 1967, "Sgt. Pepper"),
    Tracer("here, there and everywhere", 1966, "Revolver"),
    Tracer("all you need is love", 1967, "single"),
    Tracer("a day in the life", 1967, "Sgt. Pepper"),
    Tracer("here comes the sun", 1969, "Abbey Road"),
    Tracer("across the universe", 1969),
    Tracer("can't buy me love", 1964),

    # Ordinary English: NEGATIVE CONTROLS. A working method must reject these,
    # because their pre-release rate should be close to their post-release rate.
    Tracer("come together", 1969, "NEGATIVE CONTROL: common phrase"),
    Tracer("let it be", 1970, "NEGATIVE CONTROL: common phrase"),
    Tracer("getting better", 1967, "NEGATIVE CONTROL: common phrase"),
    Tracer("the word", 1965, "NEGATIVE CONTROL: extremely common"),
]

NEGATIVE_CONTROLS = {t.phrase for t in BEATLES if "NEGATIVE CONTROL" in t.note}
DISTINCTIVE = [t for t in BEATLES if t.phrase not in NEGATIVE_CONTROLS]
