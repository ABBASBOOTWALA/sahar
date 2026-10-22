"""An expanded set of concepts with independently documented origins.

The project has been limited to three usable calibration points. The cultural
tracer route was expected to fix that and does not: tracer_study.py shows song
phrases and scientific concepts are not exchangeable, with intercepts 44 years
apart. The only remaining route is to assemble more documented-origin concepts
by hand, which is what this module does.

Selection criteria, following Kashf section 9. A usable case needs a phrase that
occurs in the corpus, no older unrelated sense, no mis-dated records, and an
origin documented outside the data. Only the fourth can be supplied by a person;
the screens decide the rest, so candidates here are deliberately over-inclusive.

Candidates were also chosen to span a wide range of literature size, because
tracer_study.py found detection error correlates with document volume at
rho = -0.884. A control set clustered at one volume could not fit that.

ORIGIN DATES ARE THE GROUND TRUTH AND ARE NOT YET VERIFIED. They are recorded
here with a source so each can be checked against it before publication. Cases
where the field does not agree on a single origin are marked CONTESTED in the
note and excluded by default, because a disputed date cannot calibrate anything.
"""
from .concepts import Concept

CANDIDATES = [
    # --- computing and information ---
    Concept("public key cryptography",
            ("public key cryptography", "public-key cryptography"), 1976,
            "CONTESTED: Diffie and Hellman 1976, but Ellis at GCHQ 1970-73, declassified 1997.",
            "science-first", True),
    Concept("simulated annealing", ("simulated annealing",), 1983,
            "Kirkpatrick, Gelatt and Vecchi, Science 220(4598).",
            "science-first", True),
    Concept("genetic programming", ("genetic programming",), 1992,
            "Koza, Genetic Programming, MIT Press.", "science-first", True),
    Concept("support vector machine",
            ("support vector machine", "support vector machines"), 1992,
            "Boser, Guyon and Vapnik, COLT 1992.", "science-first", True),
    Concept("quantum teleportation", ("quantum teleportation",), 1993,
            "Bennett et al., Physical Review Letters 70(13).", "science-first", True),
    Concept("world wide web", ("world wide web",), 1989,
            "Berners-Lee, Information Management: A Proposal, CERN.",
            "science-first", True),
    Concept("convolutional neural network",
            ("convolutional neural network", "convolutional neural networks"), 1989,
            "CONTESTED: LeCun 1989, but Fukushima neocognitron 1980 is the usual precursor.",
            "science-first", True),
    Concept("long short-term memory", ("long short-term memory",), 1997,
            "Hochreiter and Schmidhuber, Neural Computation 9(8).",
            "science-first", True),
    Concept("generative adversarial network",
            ("generative adversarial network", "generative adversarial networks"), 2014,
            "Goodfellow et al., NeurIPS 2014.", "science-first", True),
    Concept("random forest", ("random forest", "random forests"), 2001,
            "CONTESTED: Breiman 2001 named it, but Ho, Random Decision Forests, 1995.", "science-first", True),
    Concept("augmented reality", ("augmented reality",), 1992,
            "Caudell and Mizell, HICSS 1992, coining the term at Boeing.",
            "science-first", True),
    Concept("virtual reality", ("virtual reality",), 1987,
            "CONTESTED: Lanier popularised it in 1987 but antecedents run to the 1930s.",
            "science-first", True),
    Concept("internet of things", ("internet of things",), 1999,
            "Ashton, presentation at Procter and Gamble.", "science-first", True),
    Concept("machine learning", ("machine learning",), 1959,
            "Samuel, IBM Journal of Research and Development 3(3).",
            "science-first", True),
    Concept("artificial intelligence", ("artificial intelligence",), 1956,
            "McCarthy et al., Dartmouth Summer Research Project proposal.",
            "science-first", True),

    # --- biology and medicine ---
    Concept("polymerase chain reaction", ("polymerase chain reaction",), 1985,
            "Saiki et al., Science 230(4732); Mullis, Nobel 1993.",
            "science-first", True),
    Concept("monoclonal antibody",
            ("monoclonal antibody", "monoclonal antibodies"), 1975,
            "Kohler and Milstein, Nature 256.", "science-first", True),
    Concept("apoptosis", ("apoptosis",), 1972,
            "Kerr, Wyllie and Currie, British Journal of Cancer 26(4).",
            "science-first", True),
    Concept("prion", ("prion", "prions"), 1982,
            "Prusiner, Science 216(4542), coining the term.", "science-first", True),
    Concept("telomerase", ("telomerase",), 1985,
            "Greider and Blackburn, Cell 43(2).", "science-first", True),
    Concept("RNA interference", ("rna interference",), 1998,
            "Fire and Mello, Nature 391.", "science-first", True),
    Concept("induced pluripotent stem cells",
            ("induced pluripotent stem cell", "induced pluripotent stem cells"), 2006,
            "Takahashi and Yamanaka, Cell 126(4).", "science-first", True),
    Concept("optogenetics", ("optogenetics",), 2006,
            "Deisseroth coins the term; Boyden et al. 2005 the method.",
            "science-first", True),
    Concept("green fluorescent protein", ("green fluorescent protein",), 1994,
            "CONTESTED: Shimomura isolated it in 1962; Chalfie 1994 made it a marker.",
            "science-first", True),
    Concept("DNA fingerprinting", ("dna fingerprinting",), 1985,
            "Jeffreys, Wilson and Thein, Nature 314.", "science-first", True),
    Concept("microbiome", ("microbiome",), 2001,
            "Lederberg and McCray, The Scientist 15(7).", "science-first", True),
    Concept("proteomics", ("proteomics", "proteome"), 1995,
            "Wilkins et al.; term coined 1994 and published 1995.",
            "science-first", True),

    # --- physics, chemistry, materials ---
    Concept("buckminsterfullerene",
            ("buckminsterfullerene", "buckminsterfullerenes"), 1985,
            "Kroto, Heath, OBrien, Curl and Smalley, Nature 318.",
            "science-first", True),
    Concept("carbon nanotube", ("carbon nanotube", "carbon nanotubes"), 1991,
            "CONTESTED: Iijima 1991, but Radushkevich and Lukyanovich 1952 per Carbon editorial.", "science-first", True),
    Concept("scanning tunneling microscopy",
            ("scanning tunneling microscopy", "scanning tunnelling microscopy"), 1981,
            "Binnig and Rohrer, IBM Zurich; Nobel 1986.", "science-first", True),
    Concept("Bose-Einstein condensate",
            ("bose-einstein condensate", "bose-einstein condensation"), 1995,
            "CONTESTED: predicted 1924-25, first realised by Anderson et al. 1995.",
            "science-first", True),
    Concept("dark energy", ("dark energy",), 1998,
            "Turner coins the term following the accelerating expansion results.",
            "science-first", True),
    Concept("high temperature superconductivity",
            ("high temperature superconductivity",
             "high-temperature superconductivity"), 1986,
            "Bednorz and Muller, Zeitschrift fur Physik B 64.", "science-first", True),
    Concept("quark", ("quark", "quarks"), 1964,
            "Gell-Mann, Physics Letters 8(3).", "science-first", True),

    # --- mathematics and systems ---
    Concept("fuzzy set", ("fuzzy set", "fuzzy sets", "fuzzy logic"), 1965,
            "Zadeh, Fuzzy sets, Information and Control 8(3).", "science-first", True),
    Concept("catastrophe theory", ("catastrophe theory",), 1972,
            "Thom, Stabilite structurelle et morphogenese.", "science-first", True),
    Concept("strange attractor", ("strange attractor", "strange attractors"), 1971,
            "Ruelle and Takens, Communications in Mathematical Physics 20(3).",
            "science-first", True),
    Concept("wavelet transform", ("wavelet transform",), 1984,
            "Grossmann and Morlet, SIAM Journal on Mathematical Analysis 15(4).",
            "science-first", True),
    Concept("Monte Carlo method",
            ("monte carlo method", "monte carlo simulation"), 1949,
            "Metropolis and Ulam, Journal of the American Statistical Association 44.",
            "science-first", True),
    Concept("cybernetics", ("cybernetics",), 1948,
            "Wiener, Cybernetics: Or Control and Communication.", "science-first", True),
    Concept("game theory", ("game theory",), 1944,
            "CONTESTED: von Neumann and Morgenstern 1944, but von Neumann 1928 precedes.",
            "science-first", True),
    Concept("Nash equilibrium", ("nash equilibrium",), 1950,
            "CONTESTED: Nash, PNAS 36(1); the eponym came into use much later.",
            "science-first", True),
]

#: Candidates whose origin the field broadly agrees on.
UNCONTESTED = [c for c in CANDIDATES if not c.origin_note.startswith("CONTESTED")]

#: Candidates whose origin is disputed. Excluded by default: a date the field
#: argues about cannot serve as ground truth for anything.
CONTESTED = [c for c in CANDIDATES if c.origin_note.startswith("CONTESTED")]
