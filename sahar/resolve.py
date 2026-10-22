"""Disambiguation strategies.

The problem these exist to solve: the science corpus holds 320 million documents
spanning centuries, so essentially any term has an older unrelated technical
sense somewhere in it. Measured examples from this corpus:

  holography      -> "Holographic Wills", 1924. A holograph is a handwritten
                     document, a legal term centuries older than Gabor.
  kinetic         -> Einstein on Brownian motion, 1905; Kelvin on the kinetic
                     theory of energy, 1874.
  artificial life -> vitalism papers of 1907 and 1911.

Each collision hands the science side a spurious early onset, which tips the
comparison science-first. That single mechanism explains why science preceded art
in 8 of 8 concepts in the first run and 7 of 8 in the second, across two entirely
different concept sets.

Strategies share one interface so they can be scored against each other rather
than argued about.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import openalex


@dataclass
class Strategy:
    name: str
    description: str

    def filters(self, concept) -> list[str]:
        raise NotImplementedError

    def counts(self, concept):
        return openalex.year_counts(self.filters(concept))


class Unfiltered(Strategy):
    """Baseline: the naive approach the pilot used."""

    def __init__(self):
        super().__init__("unfiltered", "Phrase match, no disambiguation.")

    def filters(self, concept):
        return [f"title_and_abstract.search:{openalex.phrase_query(concept.terms)}",
                openalex.exclude_leonardo()]


class FieldFilter(Strategy):
    """Restrict to broad STEM fields. Coarse: cannot separate kinetic art from
    kinetic theory, since both sit under physics."""

    STEM = [11, 12, 13, 16, 17, 21, 22, 25, 27, 31]

    def __init__(self):
        super().__init__("field", "Restricted to broad STEM fields.")

    def filters(self, concept):
        ids = "|".join(f"https://openalex.org/fields/{i}" for i in self.STEM)
        return Unfiltered().filters(concept) + [f"primary_topic.field.id:{ids}"]


class PhraseStrict(Strategy):
    """Only the unambiguous multi-word forms, dropping single-word variants.
    'holographic' collides with wills; 'digital holography' does not."""

    def __init__(self):
        super().__init__("phrase", "Multi-word phrases only, single words dropped.")

    def filters(self, concept):
        strict = [t for t in concept.terms if " " in t] or concept.terms
        return [f"title_and_abstract.search:{openalex.phrase_query(strict)}",
                openalex.exclude_leonardo()]


class TopicAnchored(Strategy):
    """Learn the concept's topic profile from its modern, unambiguous usage, then
    require historical documents to sit in those same topics.

    The reasoning: recent usage of a term is dominated by its current sense, and
    the homonyms that pollute the early record belong to different topics. So the
    present can be used to define what the concept *is*, and that definition
    applied backwards. No language model required.
    """

    def __init__(self, anchor_from=2000, top_n=6):
        super().__init__(f"topic-anchored(n={top_n})",
                         "Topic profile learned from modern usage, applied to all years.")
        self.anchor_from = anchor_from
        self.top_n = top_n
        self._cache = {}

    def profile(self, concept):
        """The concept's dominant topics, learned from recent documents only."""
        if concept.name in self._cache:
            return self._cache[concept.name]
        base = Unfiltered().filters(concept) + [f"publication_year:>{self.anchor_from - 1}"]
        tops = openalex.group_by(base, "primary_topic.id")
        chosen = [(k, n) for k, n, _ in
                  [(k, name, c) for k, name, c in tops][: self.top_n]]
        ids = [k for k, _, _ in tops[: self.top_n]]
        labels = [name for _, name, _ in tops[: self.top_n]]
        self._cache[concept.name] = (ids, labels)
        return ids, labels

    def filters(self, concept):
        ids, _ = self.profile(concept)
        if not ids:
            return Unfiltered().filters(concept)
        return Unfiltered().filters(concept) + ["primary_topic.id:" + "|".join(ids)]


class PhraseField(Strategy):
    """Multi-word phrases restricted to STEM fields.

    Best scoring strategy at time of writing: MAE 8.0 years against the six
    documented controls, against 25.0 for no disambiguation, with nothing
    censored. The two constraints address different collisions. The phrase
    constraint removes single-word senses ('holographic' alone catches wills);
    the field constraint removes whole disciplines that share the vocabulary.

    Full ranking from evaluate.py, mean absolute error over the six controls:
    phrase+field 8.0, phrase alone 13.2, field alone 20.0, topic-anchored 23.8,
    unfiltered 25.0. Only phrase+field leaves nothing censored.

    Anchoring on a modern topic profile is the worst of the filtered options. It
    scores 23.8 and censors one control, because a topic assignment reflects how
    the literature is classified now and not how it read at the time.
    """

    def __init__(self):
        super().__init__("phrase+field", "Multi-word phrases, restricted to STEM fields.")

    def filters(self, concept):
        ids = "|".join(f"https://openalex.org/fields/{i}" for i in FieldFilter.STEM)
        return PhraseStrict().filters(concept) + [f"primary_topic.field.id:{ids}"]


ALL = [Unfiltered(), FieldFilter(), PhraseStrict(), TopicAnchored(), PhraseField()]

#: The strategy selected by evaluation. Changing this requires re-running
#: evaluate.py and recording the new scores.
DEFAULT = PhraseField()
